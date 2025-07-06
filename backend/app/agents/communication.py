from typing import List, Dict, Any
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import SessionLocal
from app.models import Subscription, PortfolioRecommendation, UserProfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import google.generativeai as genai
from app.utils import send_telegram_message
import httpx


class CommunicationAgent:
    """
    Agente Comunicación - Muestra monedas, noticias y registra suscripción.
    Sistema de suscripción y publicación, enviar mensaje a cada usuario diariamente 
    de top 5 monedas (sin Twilio - solo email y frontend).
    """
    
    def __init__(self):
        self.db = SessionLocal()
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        
        # Configurar Gemini
        self.gemini_api_key = "AIzaSyDOX2Bd28ncFJaWZrWQY1wrw_SQWgc0-8U"
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def register_subscription(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Registrar suscripción para recibir reportes por Telegram"""
        try:
            existing_sub = self.db.query(Subscription).filter(
                Subscription.user_id == user_data['user_id']
            ).first()

            if existing_sub:
                # Actualizar suscripción existente
                existing_sub.email = user_data.get('email', existing_sub.email)
                existing_sub.phone = user_data.get('phone', existing_sub.phone)
                existing_sub.notification_type = user_data.get('notification_type', existing_sub.notification_type)
                existing_sub.frequency = user_data.get('frequency', existing_sub.frequency)
                existing_sub.telegram_pending = True
                existing_sub.is_active = False
                existing_sub.updated_at = datetime.now()
                message = "Suscripción actualizada. Abre el bot de Telegram y escribe /start para activarla."
            else:
                # Crear nueva suscripción
                subscription = Subscription(
                    user_id=user_data['user_id'],
                    email=user_data.get('email'),
                    phone=user_data.get('phone'),
                    notification_type=user_data.get('notification_type', 'email'),
                    frequency=user_data.get('frequency', 'daily'),
                    telegram_pending=True,
                    is_active=False
                )
                self.db.add(subscription)
                message = "Suscripción iniciada. Abre el bot de Telegram y escribe /start para activarla."

            # Verificar si existe el perfil de usuario
            user_profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_data['user_id']
            ).first()

            if not user_profile:
                user_profile = UserProfile(
                    user_id=user_data['user_id'],
                    email=user_data.get('email'),
                    telefono=user_data.get('phone'),
                    risk_tolerance=user_data.get('risk_tolerance', 'moderate'),
                    investment_amount=user_data.get('investment_amount', 1000),
                    investment_horizon=user_data.get('investment_horizon', 'medium'),
                    preferred_sectors=json.dumps(user_data.get('preferred_sectors', [])),
                    is_subscribed=True
                )
                self.db.add(user_profile)
            else:
                # Actualizar perfil
                user_profile.email = user_data.get('email', user_profile.email)
                user_profile.telefono = user_data.get('phone', user_profile.telefono)
                user_profile.risk_tolerance = user_data.get('risk_tolerance', user_profile.risk_tolerance)
                user_profile.investment_amount = user_data.get('investment_amount', user_profile.investment_amount)
                user_profile.investment_horizon = user_data.get('investment_horizon', user_profile.investment_horizon)
                user_profile.preferred_sectors = json.dumps(
                    user_data.get('preferred_sectors', json.loads(user_profile.preferred_sectors or '[]'))
                )
                user_profile.is_subscribed = True
                user_profile.updated_at = datetime.now()

            self.db.commit()

            return {
                'success': True,
                'message': message,
                'subscription_id': existing_sub.id if existing_sub else subscription.id
            }

        except Exception as e:
            self.db.rollback()
            return {
                'success': False,
                'message': f'Error registrando suscripción: {str(e)}'
            }
        finally:
            self.db.close()


    
    def unsubscribe_user(self, user_id: str) -> Dict[str, Any]:
        """Cancelar suscripción de usuario"""
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.user_id == user_id
            ).first()
            
            if subscription:
                subscription.is_active = False
                subscription.updated_at = datetime.now()
                
                # Actualizar perfil de usuario
                user_profile = self.db.query(UserProfile).filter(
                    UserProfile.user_id == user_id
                ).first()
                
                if user_profile:
                    user_profile.is_subscribed = False
                    user_profile.updated_at = datetime.now()
                
                self.db.commit()
                
                return {
                    'success': True,
                    'message': 'Suscripción cancelada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'No se encontró suscripción activa'
                }
                
        except Exception as e:
            self.db.rollback()
            return {
                'success': False,
                'message': f'Error cancelando suscripción: {str(e)}'
            }
        finally:
            self.db.close()
    
    def get_active_subscribers(self, frequency: str = 'daily') -> List[Dict[str, Any]]:
        """Obtener lista de suscriptores activos por frecuencia"""
        try:
            subscribers = self.db.query(Subscription, UserProfile).join(
                UserProfile, Subscription.user_id == UserProfile.user_id
            ).filter(
                Subscription.is_active == True,
                Subscription.frequency == frequency,
                UserProfile.is_subscribed == True
            ).all()
            
            return [
                {
                    'user_id': sub.user_id,
                    'email': sub.email,
                    'phone': sub.phone,
                    'notification_type': sub.notification_type,
                    'risk_tolerance': profile.risk_tolerance,
                    'investment_amount': profile.investment_amount,
                    'investment_horizon': profile.investment_horizon,
                    'preferred_sectors': json.loads(profile.preferred_sectors or '[]')
                }
                for sub, profile in subscribers
            ]
            
        except Exception as e:
            print(f"Error obteniendo suscriptores: {e}")
            return []
        finally:
            self.db.close()
    
    def send_email_notification(self, recipient_email: str, subject: str, 
                              html_content: str, text_content: str = None) -> bool:
        """Enviar notificación por email"""
        try:
            if not self.email_user or not self.email_password:
                print("Credenciales de email no configuradas")
                return False
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_user
            msg['To'] = recipient_email
            
            # Crear partes del mensaje
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error enviando email a {recipient_email}: {e}")
            return False
    
    def generate_portfolio_email(self, user_data: Dict[str, Any], 
                               recommendation: Dict[str, Any]) -> Dict[str, str]:
        """Generar contenido del email con recomendaciones de portfolio"""
        
        user_name = user_data.get('user_id', 'Usuario')
        recommended_coins = recommendation.get('recommended_coins', [])
        expected_return = recommendation.get('expected_return', 0)
        risk_score = recommendation.get('risk_score', 0)
        
        # Contenido HTML
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; color: #2c3e50; margin-bottom: 30px; }}
                .coin-item {{ background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #3498db; }}
                .metrics {{ background-color: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #7f8c8d; margin-top: 30px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 CriptoAI - Tu Portfolio Personalizado</h1>
                    <p>Hola {user_name}, aquí tienes tus recomendaciones diarias</p>
                </div>
                
                <h2>💰 Top 5 Criptomonedas Recomendadas:</h2>
        """
        
        for i, coin in enumerate(recommended_coins, 1):
            html_content += f"""
                <div class="coin-item">
                    <h3>{i}. {coin['name']} ({coin['symbol']})</h3>
                    <p><strong>Asignación recomendada:</strong> {coin['allocation_percentage']}%</p>
                    <p><strong>Precio actual:</strong> ${coin['current_price']:,.4f}</p>
                    <p><strong>Market Cap:</strong> ${coin['market_cap']:,}</p>
                </div>
            """
        
        html_content += f"""
                <div class="metrics">
                    <h3>📊 Métricas del Portfolio:</h3>
                    <p><strong>Retorno Esperado:</strong> {expected_return}%</p>
                    <p><strong>Score de Riesgo:</strong> {risk_score}/100</p>
                    <p><strong>Nivel de Confianza:</strong> {recommendation.get('confidence_level', 0)}%</p>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <p><strong>⚠️ Disclaimer:</strong> Esta información es solo para fines educativos y no constituye asesoramiento financiero. Siempre realiza tu propia investigación antes de invertir.</p>
                </div>
                
                <div class="footer">
                    <p>CriptoAI © 2025 - Sistema de Análisis y Optimización de Criptomonedas</p>
                    <p>Para cancelar suscripción, responde con "UNSUBSCRIBE"</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Contenido de texto plano
        text_content = f"""
        CriptoAI - Portfolio Personalizado
        
        Hola {user_name},
        
        Top 5 Criptomonedas Recomendadas:
        """
        
        for i, coin in enumerate(recommended_coins, 1):
            text_content += f"""
        {i}. {coin['name']} ({coin['symbol']})
           - Asignación: {coin['allocation_percentage']}%
           - Precio: ${coin['current_price']:,.4f}
           - Market Cap: ${coin['market_cap']:,}
        """
        
        text_content += f"""
        
        Métricas del Portfolio:
        - Retorno Esperado: {expected_return}%
        - Score de Riesgo: {risk_score}/100
        - Nivel de Confianza: {recommendation.get('confidence_level', 0)}%
        
        DISCLAIMER: Esta información es solo para fines educativos.
        
        CriptoAI © 2025
        """
        
        return {
            'subject': f'🚀 CriptoAI - Tus recomendaciones del {datetime.now().strftime("%d/%m/%Y")}',
            'html_content': html_content,
            'text_content': text_content
        }
    
    async def send_daily_recommendations(self) -> Dict[str, Any]:
        """Enviar recomendaciones diarias a todos los suscriptores"""
        try:
            subscribers = self.get_active_subscribers('daily')
            
            if not subscribers:
                return {
                    'success': True,
                    'message': 'No hay suscriptores activos para notificaciones diarias',
                    'sent_count': 0
                }
            
            sent_count = 0
            failed_count = 0
            
            for subscriber in subscribers:
                try:
                    # Obtener la recomendación más reciente para este usuario
                    latest_recommendation = self.db.query(PortfolioRecommendation).filter(
                        PortfolioRecommendation.user_id == subscriber['user_id']
                    ).order_by(PortfolioRecommendation.created_at.desc()).first()
                    
                    if not latest_recommendation:
                        print(f"No hay recomendaciones para usuario {subscriber['user_id']}")
                        continue
                    
                    # Preparar datos de recomendación
                    recommendation_data = {
                        'recommended_coins': json.loads(latest_recommendation.recommended_coins),
                        'expected_return': latest_recommendation.expected_return,
                        'risk_score': latest_recommendation.risk_score,
                        'confidence_level': latest_recommendation.confidence_level
                    }
                    
                    # Generar contenido del email
                    email_content = self.generate_portfolio_email(subscriber, recommendation_data)
                    
                    # Enviar notificación según preferencia
                    if subscriber['notification_type'] in ['email', 'both'] and subscriber['email']:
                        success = self.send_email_notification(
                            subscriber['email'],
                            email_content['subject'],
                            email_content['html_content'],
                            email_content['text_content']
                        )
                        
                        if success:
                            sent_count += 1
                        else:
                            failed_count += 1
                    
                    # TODO: Implementar SMS si es necesario (sin Twilio)
                    # if subscriber['notification_type'] in ['sms', 'both'] and subscriber['phone']:
                    #     send_sms_notification(subscriber['phone'], sms_content)
                    
                except Exception as e:
                    print(f"Error enviando notificación a {subscriber['user_id']}: {e}")
                    failed_count += 1
            
            return {
                'success': True,
                'message': f'Notificaciones enviadas: {sent_count}, Fallidas: {failed_count}',
                'sent_count': sent_count,
                'failed_count': failed_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error enviando recomendaciones diarias: {str(e)}'
            }
        finally:
            self.db.close()
    
    def get_user_notifications_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener historial de notificaciones de un usuario"""
        try:
            recommendations = self.db.query(PortfolioRecommendation).filter(
                PortfolioRecommendation.user_id == user_id
            ).order_by(PortfolioRecommendation.created_at.desc()).limit(limit).all()
            
            return [
                {
                    'id': rec.id,
                    'recommended_coins': json.loads(rec.recommended_coins),
                    'expected_return': rec.expected_return,
                    'risk_score': rec.risk_score,
                    'confidence_level': rec.confidence_level,
                    'created_at': rec.created_at.isoformat()
                }
                for rec in recommendations
            ]
            
        except Exception as e:
            print(f"Error obteniendo historial de usuario {user_id}: {e}")
            return []
        finally:
            self.db.close()
    
    def generate_portfolio_report_with_ai(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generar reporte explicativo del portfolio usando Gemini AI"""
        try:
            # Extraer datos del portfolio
            portfolio_metrics = portfolio_data.get('portfolio_metrics', {})
            portfolio_optimization = portfolio_data.get('portfolio_optimization', {})
            user_profile = portfolio_data.get('user_profile', {})
            
            expected_return = portfolio_metrics.get('expected_return', 0)
            risk_score = portfolio_metrics.get('risk_score', 0)
            confidence_level = portfolio_metrics.get('confidence_level', 0)
            
            top_coins = portfolio_optimization.get('top_4_coins', [])
            allocation_percentages = portfolio_optimization.get('allocation_percentages', {})
            investment_amounts = portfolio_optimization.get('investment_amounts', {})
            total_investment = portfolio_optimization.get('total_investment', 0)
            
            # Crear prompt para Gemini
            prompt = f"""
Eres un asesor financiero experto en criptomonedas. Analiza este portfolio de inversión y genera un reporte explicativo en español para un usuario de nivel {user_profile.get('risk_tolerance', 'moderate')} con horizonte de inversión {user_profile.get('investment_horizon', 'medium')}.

DATOS DEL PORTFOLIO:
- Monto total de inversión: ${total_investment:,.2f}
- Retorno esperado: {expected_return}%
- Score de riesgo: {risk_score}/100
- Nivel de confianza: {confidence_level}%

COMPOSICIÓN DEL PORTFOLIO:
"""
            
            for coin in top_coins:
                prompt += f"""
- {coin['symbol']}:
  * Asignación: {coin['allocation_percentage']}%
  * Monto de inversión: ${investment_amounts.get(coin['symbol'], 0):,.2f}
  * Precio actual: ${coin['current_price']:,.4f}
  * Score de inversión: {coin['investment_score']}/100
  * Score de riesgo: {coin['risk_score']}/100
  * Retorno esperado: {coin['expected_return']}%
  * Volatilidad: {coin['volatility']}%
  * Score de estabilidad: {coin['stability_score']}/100
  * Sentimiento del mercado: {coin['market_sentiment']}
  * Cambio en 24h: {coin['price_change_24h']}%
"""

            prompt += """

INSTRUCCIONES PARA EL REPORTE:
1. Explica en lenguaje sencillo y profesional qué significa esta composición de portfolio
2. Analiza los riesgos y oportunidades de cada criptomoneda
3. Explica el significado del retorno esperado negativo si aplica
4. Proporciona recomendaciones sobre la diversificación
5. Incluye advertencias importantes sobre la volatilidad del mercado de criptomonedas
6. Termina con un resumen ejecutivo de máximo 3 puntos clave
7. Usa un tono profesional pero accesible
8. Incluye emojis apropiados para hacer el reporte más visual
9. Debe tener 100 palabras como máximo

Debe estar estructurado con encabezados claros.
"""

            # Generar reporte con Gemini
            response = self.model.generate_content(prompt)
            ai_report = response.text
            
            return {
                'success': True,
                'ai_report': ai_report,
                'generated_at': datetime.now().isoformat(),
                'portfolio_summary': {
                    'total_investment': total_investment,
                    'expected_return': expected_return,
                    'risk_score': risk_score,
                    'confidence_level': confidence_level,
                    'top_coins_count': len(top_coins),
                    'user_profile': user_profile
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error generando reporte con IA: {str(e)}',
                'ai_report': None
            }
    

    async def send_scheduled_telegram_reports(self, db: Session):
        """
        Enviar reportes por Telegram según frecuencia y suscripción.
        """
        hoy = datetime.utcnow()
        dia_semana = hoy.strftime('%A').lower()
        dia_mes = hoy.day

        # Obtener todas las suscripciones activas
        subscripciones = db.query(Subscription).filter(
            Subscription.is_active == True,
        ).all()

        for sub in subscripciones:
            if not sub.chat_id:
                continue

            # Validar si corresponde enviar hoy según frecuencia
            enviar = (
                sub.frequency == "daily" or
                (sub.frequency == "weekly" and dia_semana == "monday") or
                (sub.frequency == "monthly" and dia_mes == 1)
            )

            if not enviar:
                continue

            # Obtener perfil asociado por user_id
            user_profile = db.query(UserProfile).filter(UserProfile.user_id == sub.user_id).first()
            if not user_profile:
                continue

            try:
                # Llamar al endpoint que genera el reporte de portafolio
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        "http://localhost:8000/api/generate-portfolio-report",
                        json={"id": user_profile.id},
                        timeout=30.0
                    )
                    resp.raise_for_status()
                    result = resp.json()

                if result.get("success"):
                    # Construir mensaje de Telegram
                    mensaje = (
                        f"📈 *CryptoAdvisor - Tu reporte de inversión diario*\n\n"
                        f"{result['ai_report']}\n\n"
                        f"🕒 Generado el: {result['generated_at']}"
                    )

                    result_telegram = await send_telegram_message(chat_id=sub.chat_id, text=mensaje)

                    if not result_telegram.get("success"):
                        print(f"[❌] Error al enviar a {sub.chat_id}: {result_telegram.get('error')}")
                    else:
                        print(f"[✅] Reporte enviado a chat_id {sub.chat_id}")

            except Exception as e:
                print(f"[❌] Error al procesar chat_id={sub.chat_id}: {e}")
