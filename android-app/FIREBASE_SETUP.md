# Firebase setup: registration and blog push notifications

The app uses **Firebase** for:

1. **Registration** – name, email, password (Firebase Authentication).
2. **Push notifications** – when a new blog post is published (Firebase Cloud Messaging + a scheduled Cloud Function).

You need a **Firebase project** and a few one-time setup steps.

---

## 1. Create a Firebase project

1. Go to [Firebase Console](https://console.firebase.google.com/).
2. Click **Add project** (or use an existing project). Name it e.g. **Faith Driven Life**.
3. Follow the steps (Google Analytics is optional). Create the project.

---

## 2. Add the Android app to Firebase

1. In the project overview, click the **Android** icon to add an Android app.
2. **Android package name:** `com.faithdrivenlife.app` (must match exactly).
3. App nickname and Debug signing certificate are optional. Click **Register app**.
4. **Download `google-services.json`** and place it in your Android project:
   - Put the file in: `android-app/app/google-services.json`
   - Do **not** commit this file to a public repo if you prefer to keep your project ID private (add `app/google-services.json` to `.gitignore`).
5. Click **Next** until you finish the wizard.

---

## 3. Enable Authentication and Firestore

1. In the Firebase Console left menu, go to **Build → Authentication**.
2. Click **Get started**, then open the **Sign-in method** tab.
3. Enable **Email/Password** (first provider in the list). Save.

4. Go to **Build → Firestore Database**.
5. Click **Create database**. Choose **Start in test mode** (you can tighten rules later). Pick a region and enable.

---

## 4. Get the FCM server key (optional, for testing)

- For **topic** messages (used by the Cloud Function), you do **not** need a server key in the app. The scheduled function runs inside Firebase and uses the Admin SDK.

---

## 5. Deploy the Cloud Function (sends “new blog” notifications)

The function in `firebase-functions/` checks the Blogger feed every 6 hours and sends a push to the **new_blog** topic when there is a new post.

1. Install the [Firebase CLI](https://firebase.google.com/docs/cli):  
   `npm install -g firebase-tools`
2. Log in:  
   `firebase login`
3. From the **`android-app`** folder (the one that contains `firebase-functions` and `firebase.json`), run:  
   `firebase use --add`  
   and select your Firebase project.
4. Go into the functions folder and install dependencies:  
   `cd firebase-functions`  
   `npm install`
5. Deploy only functions:  
   `cd ..`  
   `firebase deploy --only functions`

After deployment, the scheduler will run **newBlogCheck** every 6 hours. You can also trigger it once from the Firebase Console (**Functions → newBlogCheck → Run**).

---

## 6. Build and run the app

1. Open the **android-app** project in Android Studio (with `google-services.json` in place).
2. Sync Gradle. Resolve any errors (e.g. if a dependency version is incompatible).
3. Run the app on a device or emulator.

---

## 7. How it works for users

1. User opens the app and taps the **⋮** menu → **Register for blog notifications**.
2. They enter **name**, **email**, and **password** (min 6 characters) and tap **Create account**.
3. Firebase Auth creates the account; the app subscribes the device to the FCM topic **new_blog**.
4. When the Cloud Function runs and finds a new post on the Blogger feed, it sends a message to **new_blog**. All registered devices receive a push notification (e.g. “New blog post: &lt;title&gt;”). Tapping the notification opens the app to the blogs page or the post URL.

---

## Changing the blog feed or schedule

- **Blog feed:** Edit `firebase-functions/index.js`: change `BLOGGER_FEED_URL` and, if needed, `SITE_BLOGS_URL`.
- **Schedule:** In `index.js`, change `every 6 hours` to e.g. `every 12 hours` or `every 1 hours` (see [Cloud Scheduler syntax](https://cloud.google.com/scheduler/docs/configuring/cron-job-schedules)).

---

## Troubleshooting

- **“Default FirebaseApp is not initialized”**  
  Make sure `google-services.json` is in `app/` and that the app-level `build.gradle` applies the Google services plugin.
- **No notifications received**  
  Confirm the function deployed successfully and that the device is subscribed to **new_blog** (registration flow completed). On Android 13+, ensure the app has notification permission.
- **Registration fails**  
  Check that Email/Password sign-in is enabled in Firebase Authentication.
