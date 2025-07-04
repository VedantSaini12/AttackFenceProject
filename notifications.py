# notifications.py
import streamlit as st
import mysql.connector as connector
from datetime import datetime
from typing import List, Dict, Any

# Note: Using st.session_state to hold the db connection is often more robust
# in complex apps than @st.cache_resource for short-lived connections.
def get_notification_db_connection():
    if 'db_connection' not in st.session_state or st.session_state.db_connection.is_connected() == False:
        try:
            st.session_state.db_connection = connector.connect(
                host="localhost",
                user="root", 
                password="password",
                database="auth"
            )
        except connector.Error:
            st.error("Database connection failed for notifications.")
            return None
    return st.session_state.db_connection

def create_notifications_table():
    """Create notifications table if it doesn't exist"""
    db = get_notification_db_connection()
    if db:
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                recipient VARCHAR(100) NOT NULL,
                sender VARCHAR(100),
                message TEXT NOT NULL,
                notification_type VARCHAR(50) NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                related_id INT,
                INDEX idx_recipient (recipient),
                INDEX idx_is_read (is_read)
            )
        """)
        db.commit()
        cursor.close()

def add_notification(recipient: str, message: str, notification_type: str, sender: str = None, related_id: int = None):
    """Add a new notification. This should be called when an event happens."""
    db = get_notification_db_connection()
    if db:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO notifications (recipient, sender, message, notification_type, related_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (recipient, sender, message, notification_type, related_id))
        db.commit()
        cursor.close()

def get_user_notifications(username: str) -> List[Dict[str, Any]]:
    """Get all notifications for a user"""
    db = get_notification_db_connection()
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM notifications WHERE recipient = %s ORDER BY created_at DESC", (username,))
        notifications = cursor.fetchall()
        cursor.close()
        return notifications
    return []

def mark_all_read(username: str):
    """Mark all notifications as read for a user"""
    db = get_notification_db_connection()
    if db:
        cursor = db.cursor()
        cursor.execute("UPDATE notifications SET is_read = TRUE WHERE recipient = %s", (username,))
        db.commit()
        cursor.close()

def notification_bell_component(username: str):
    """
    Renders the notification bell and its popover using a reliable emoji-based button.
    """
    # Initialize the notifications table on first run
    create_notifications_table()
    
    # Get notifications and unread count
    notifications = get_user_notifications(username)
    unread_count = sum(1 for n in notifications if not n['is_read'])
    
    # --- CSS for styling the popover button and notification items ---
    st.markdown("""
    <style>
        /* Container for the popover to position it */
        div[data-testid="stPopover"] {
            position: fixed;
            top: 120px;      /* Adjusted position */
            left: 1400px;    /* Adjusted position */
            z-index: 999;
        }

        /* The button that opens the popover */
        div[data-testid="stPopover"] > button {
            font-size: 1.5rem; /* Make emoji larger */
            padding: 0.5rem;
            width: 55px;
            height: 55px;
            border-radius: 50%;
            transition: all 0.2s ease-in-out;
            animation: none; /* remove previous animations */
        }
        
        div[data-testid="stPopover"] > button:hover {
            transform: scale(1.1);
        }

        /* Styles for each notification inside the popover */
        .notification-item { 
            padding: 1rem 0.5rem; 
            margin-bottom: 10px; 
            border-bottom: 1px solid #e2e8f0;
        }
        .notification-item.unread { 
            background-color: #f0f8ff; /* Light blue background for unread */
            border-left: 4px solid #007bff;
            padding-left: 1rem;
            border-radius: 4px;
        }
        .notification-message { font-size: 14px; margin-bottom: 5px; color: #333; }
        .notification-time { font-size: 12px; color: #666; }
    </style>
    """, unsafe_allow_html=True)
    
    # --- Create the label for the popover button ---
    # Combine the bell emoji with the unread count for a simple, effective badge
    popover_label = f"🔔 {unread_count}" if unread_count > 0 else "🔔"
    
    # --- Streamlit Popover Component ---
    with st.popover(popover_label):
        st.header("Notifications")
        
        # Add the "Mark All Read" button only if there are unread notifications
        if unread_count > 0:
            if st.button("Mark All As Read", use_container_width=True, type="primary"):
                mark_all_read(username)
                st.rerun()
        
        st.divider()

        # Display notifications
        if not notifications:
            st.info("You have no notifications.")
        else:
            for n in notifications:
                read_class = "unread" if not n['is_read'] else ""
                time_str = n['created_at'].strftime("%b %d, %Y at %I:%M %p")
                st.markdown(f"""
                <div class="notification-item {read_class}">
                    <div class="notification-message">{n['message']}</div>
                    <div class="notification-time">{time_str}</div>
                </div>
                """, unsafe_allow_html=True)