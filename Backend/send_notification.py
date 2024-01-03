import requests
import firebase_admin
from firebase_functions import db_fn, https_fn, firestore_fn
from firebase_admin import initialize_app, firestore, auth, db, messaging, credentials

@firestore_fn.on_document_updated(document="posts/{pushID}")
def send_notification_test(event: firestore_fn.Event[firestore_fn.Change[firestore_fn.DocumentSnapshot | None],],) -> None:
    client = firestore.client()
    if event.data is None:
        return
    try:
        # hype_email_test = event.data.get("hypeUsername_test")
        hypeUsername = event.data.after.get("hypeUsername")
        opEmail = event.data.after.get("opEmail")
        query = client.collection("users").where('email', '==', opEmail)
        docs = query.stream()
        print(f"docs is: {docs}")
        for doc in docs: 
            opUID = doc.id
        notification_tokens = client.document(f"users/{opUID}").get().to_dict()["notificationTokens"]
        if client.document(f"users/{opUID}").get().to_dict()["unreadNotifications"]:
            unread_notifications = client.document(f"users/{opUID}").get().to_dict()["unreadNotifications"]
            print("field already exists for this user, and it's equal to {unread_notifications}")
        else: 
              client.document(f"users/{opUID}").set({'unreadNotifications': 0}, merge=True)
              print("field not found so it was created and set to 0")
        #dummyvar = client.document("posts/121FF917-D61E-4FF6-BA55-90E4314CB73F").get().to_dict()
        #print(f"dummy var is: {dummyvar}")
        print("event.data.after is:")
        print(hypeUsername, opEmail, opUID, notification_tokens)
        #hype_comment = event.data.after.get("hypeComment_test")
        
    except KeyError:
        # No "hypeUsername_test" field, so do nothing.
        print("change parameters not found")
        return
    
    change = event.data

    if not change.after:
        print(f"User {hypeUsername} removed their comment from post {event.params['pushID']} :")
        return

    print(f"User {hypeUsername} has left a comment on post {event.params['pushID']}")
    
    #the condition below is not applicable in my case for now
    # if (
    #     not isinstance(notification_tokens, dict)
    #     or len(notification_tokens) < 1
    # ):
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
    # msgs = [
    #     messaging.Message(token=token, notification=notification)
    #     for token in notification_tokens
    # ]

    print(notification_tokens[0])

    msg = messaging.Message(token=notification_tokens[0], notification=notification)
    messaging.send(msg)
