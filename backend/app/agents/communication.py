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
    
    def register_subscription(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Registrar nueva suscripción de usuario"""
        try:
            # Verificar si ya existe suscripción
            existing_sub = self.db.query(Subscription).filter(
                Subscription.user_id == user_data['user_id']
            ).first()
            
            if existing_sub:
                # Actualizar suscripción existente
                existing_sub.email = user_data.get('email', existing_sub.email)
                existing_sub.phone = user_data.get('phone', existing_sub.phone)
                existing_sub.notification_type = user_data.get('notification_type', existing_sub.notification_type)
                existing_sub.frequency = user_data.get('frequency', existing_sub.frequency)
                existing_sub.is_active = True
                existing_sub.updated_at = datetime.now()
                
                message = "Suscripción actualizada exitosamente"
            else:
                # Crear nueva suscripción
                subscription = Subscription(
                    user_id=user_data['user_id'],
                    email=user_data.get('email'),
                    phone=user_data.get('phone'),
                    notification_type=user_data.get('notification_type', 'email'),
                    frequency=user_data.get('frequency', 'daily'),
                    is_active=True
                )
                self.db.add(subscription)
                message = "Suscripción creada exitosamente"
            
            # Crear o actualizar perfil de usuario
            user_profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_data['user_id']
            ).first()
            
            if not user_profile:
                user_profile = UserProfile(
                    user_id=user_data['user_id'],
                    risk_tolerance=user_data.get('risk_tolerance', 'moderate'),
                    investment_amount=user_data.get('investment_amount', 1000),
                    investment_horizon=user_data.get('investment_horizon', 'medium'),
                    preferred_sectors=json.dumps(user_data.get('preferred_sectors', [])),
                    is_subscribed=True
                )
                self.db.add(user_profile)
            else:
                user_profile.risk_tolerance = user_data.get('risk_tolerance', user_profile.risk_tolerance)
                user_profile.investment_amount = user_data.get('investment_amount', user_profile.investment_amount)
                user_profile.investment_horizon = user_data.get('investment_horizon', user_profile.investment_horizon)
                user_profile.preferred_sectors = json.dumps(user_data.get('preferred_sectors', 
                                                          json.loads(user_profile.preferred_sectors or '[]')))
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
