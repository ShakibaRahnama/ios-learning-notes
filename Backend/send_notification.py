import requests
import firebase_admin
from firebase_functions import db_fn, https_fn, firestore_fn
from firebase_admin import initialize_app, firestore, auth, db, messaging, credentials

@firestore_fn.on_document_updated(document="posts/{pushID}")
def send_notification(event: firestore_fn.Event[firestore_fn.Change[firestore_fn.DocumentSnapshot | None],],) -> None:
    client = firestore.client()
    if event.data is None:
        return
    try:
        hypeUsername = event.data.after.get("hypeUsername")
        opEmail = event.data.after.get("opEmail")
        query = client.collection("users").where('email', '==', opEmail)
        docs = query.stream()
        print(f"docs is: {docs}")
        for doc in docs: 
            opUID = doc.id
        notification_tokens = client.document(f"users/{opUID}").get().to_dict()["notificationTokens"]
        
        op_data = client.document(f"users/{opUID}").get().to_dict()
        if "unread_notifications" in op_data:
            unread_notifications = op_data["unread_notifications"]+1
            print("field already exists, storing in unread notification value")
        else: 
            client.document(f"users/{opUID}").set({"unread_notifications":0})
            print("field did not exist so it was created")
            unread_notifications = 1
            
        print("event.data.after is:")
        print(hypeUsername, opEmail, opUID, notification_tokens)
        
    except KeyError:
        print("change parameters not found")
        return
    
    change = event.data

    if not change.after:
        print(f"User {hypeUsername} removed their comment from post {event.params['pushID']} :")
        return

    print(f"User {hypeUsername} has left a comment on post {event.params['pushID']}")
    
    if len(notification_tokens)<1:
        print("There are no tokens to send notifications to.")
        return
    print(
        f"There are {len(notification_tokens)} token(s) to send notifications to."
    )

    notification = messaging.Notification(
        title=f"{hypeUsername} just hyped your post!",
        body="Open the app to see what they said!",
    )

        # Send notifications to all tokens.
    msgs = [
        messaging.Message(token=token, notification=notification)
        for token in notification_tokens
    ]
    
    messaging.send(msg for msg in msgs)
