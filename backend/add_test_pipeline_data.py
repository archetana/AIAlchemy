#!/usr/bin/env python3
"""
Add test applications with different pipeline statuses
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from app.models import StartupApplication, ApplicationStatus
from app.core.config import get_settings

def main():
    settings = get_settings()
    
    # Create synchronous engine for this script - use the actual database file
    engine = create_engine('sqlite:///aialchemy.db')
    SessionLocal = sessionmaker(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Update existing apps to have different statuses
        app1 = db.query(StartupApplication).filter(StartupApplication.id == 1).first()
        if app1:
            app1.status = ApplicationStatus.DATA_PROCESSING
            app1.ai_score = 75.5
            print(f"Updated {app1.company_name} to {app1.status}")
        
        app2 = db.query(StartupApplication).filter(StartupApplication.id == 2).first()  
        if app2:
            app2.status = ApplicationStatus.AI_ANALYSIS
            app2.ai_score = 82.3
            print(f"Updated {app2.company_name} to {app2.status}")
            
        # Add new apps with different statuses
        new_apps = [
            StartupApplication(
                company_name='TechFlow Innovations',
                contact_email='contact@techflow.com',
                status=ApplicationStatus.MANUAL_REVIEW,
                ai_score=89.2,
                industry_id=1
            ),
            StartupApplication(
                company_name='DataSync Pro',
                contact_email='hello@datasync.io',
                status=ApplicationStatus.PARTNER_REVIEW,
                ai_score=76.8,
                industry_id=2
            ),
            StartupApplication(
                company_name='CloudVision AI',
                contact_email='info@cloudvision.ai',
                status=ApplicationStatus.COMPLETED,
                ai_score=91.5,
                final_rating='Strong Invest',
                industry_id=1
            )
        ]
        
        for app in new_apps:
            db.add(app)
            print(f"Added {app.company_name} with status {app.status}")
        
        db.commit()
        print('Successfully added test applications with different statuses!')
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()