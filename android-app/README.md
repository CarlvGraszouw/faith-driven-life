# A Faith Driven Life — Android App

This folder contains an Android app that wraps your website in a WebView. The app loads your live site from GitHub Pages, so any updates to the site appear in the app automatically.

## What you need

- **Android Studio** (latest stable): [developer.android.com/studio](https://developer.android.com/studio)
- **JDK 17** (usually bundled with Android Studio)

## How to build and run

**You need Android Studio** (it includes the JDK and Android SDK). Install from [developer.android.com/studio](https://developer.android.com/studio) if you haven’t.

1. Open **Android Studio**.
2. **File → Open** and select the **`android-app`** folder (the one that contains `build.gradle.kts` and `gradlew.bat`).
3. Wait for **Gradle sync** to finish (first time can take several minutes; it will download Gradle and dependencies).
4. To run on a device: connect an Android phone with **USB debugging** enabled, or start an **Android emulator** (Tools → Device Manager).
5. Click the green **Run** button (or **Shift+F10**) to build and install the app.

**From the command line (after opening the project once in Android Studio):**  
From the `android-app` folder you can run `gradlew.bat assembleDebug` if `JAVA_HOME` is set to your JDK (e.g. the one inside Android Studio).

## Building a release APK (to share or publish)

1. In Android Studio: **Build → Build Bundle(s) / APK(s) → Build APK(s)**.
2. When the build finishes, click **Locate** in the notification to open the folder. The APK is in `app/build/outputs/apk/release/`.
3. You can install this APK on any Android device (they may need to allow “Install from unknown sources” for your file manager or browser).

## App details

- **URL loaded:** `https://carlvgraszouw.github.io/faith-driven-life/`
- **Package name:** `com.faithdrivenlife.app`
- **Min Android:** 7.0 (API 24)  
- **Target Android:** 14 (API 34)

The app shows a loading bar at the top while the site loads, and the **Back** button navigates back inside the WebView when possible.

## Registration and push notifications (new blogs)

The app supports **user registration** (name, email, password) and **push notifications** when new blog posts are published.

- **In the app:** Tap the **⋮** menu → **Register for blog notifications**. Create an account to receive notifications.
- **Setup required:** You must create a Firebase project and add `google-services.json` to the `app/` folder, then deploy the included Cloud Function. Full steps: see **[FIREBASE_SETUP.md](FIREBASE_SETUP.md)**.

Without Firebase configured, the app still works as a WebView; the registration menu item will open the screen but sign-up will fail until Firebase is set up.

## Changing the app icon

The app uses a simple gold-on-dark icon. To use your own:

1. In Android Studio, right‑click `app` in the Project view.
2. Choose **New → Image Asset**.
3. Create your icon and replace the default launcher icons in `res/mipmap-*` and `res/drawable`.

## Publishing to Google Play

To publish on the Play Store you will need:

- A **Google Play Developer** account (one-time fee).
- A **release signing key** (Android Studio: **Build → Generate Signed Bundle / APK**; use “Android App Bundle” for Play).
- Store listing (description, screenshots, privacy policy if required).

The app is a WebView wrapper, so you may need to ensure your store listing and app behaviour comply with [Play Policy](https://play.google.com/about/developer-content-policy/) (e.g. no misleading behaviour, clear that it’s a web app wrapper if relevant).
