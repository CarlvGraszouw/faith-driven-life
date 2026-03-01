# Publishing to Samsung Galaxy Store (free)

This guide walks you through publishing **A Faith Driven Life** to the Samsung Galaxy Store at no cost.

## Prerequisites

- **Samsung Seller Office account** (free): [seller.samsungmobile.com](https://seller.samsungmobile.com)
- **Signed release build** of the app (AAB or APK)
- **App icon** (512×512 px) and **screenshots** (phone; optional tablet)

---

## 1. Create a release build

### Signing key (one-time)

If you don’t have a keystore yet:

```bash
keytool -genkey -v -keystore faith-driven-life-release.keystore -alias faith -keyalg RSA -keysize 2048 -validity 10000
```

Keep the keystore and password safe; you need them for every future update.

### Configure signing in the project

Create or edit `android-app/keystore.properties` (do **not** commit this file; add it to `.gitignore`):

```properties
storeFile=../faith-driven-life-release.keystore
storePassword=YOUR_STORE_PASSWORD
keyAlias=faith
keyPassword=YOUR_KEY_PASSWORD
```

In `app/build.gradle.kts`, add before the `android { }` block:

```kotlin
// Load keystore properties for release signing (optional; create keystore.properties locally)
val keystorePropertiesFile = rootProject.file("keystore.properties")
if (keystorePropertiesFile.exists()) {
    val keystoreProperties = java.util.Properties()
    keystoreProperties.load(java.io.FileInputStream(keystorePropertiesFile))
    android {
        signingConfigs {
            create("release") {
                keyAlias = keystoreProperties["keyAlias"] as String
                keyPassword = keystoreProperties["keyPassword"] as String
                storeFile = file(keystoreProperties["storeFile"] as String)
                storePassword = keystoreProperties["storePassword"] as String
            }
        }
        buildTypes {
            release {
                signingConfig = signingConfigs.getByName("release")
                // ... existing release config
            }
        }
    }
}
```

(If you prefer, you can set `signingConfig` for `release` in `buildTypes` only and keep the keystore path/passwords in a single place.)

### Build release AAB (recommended for Galaxy Store)

From the project root:

```bash
cd android-app
./gradlew bundleRelease
```

Output: `app/build/outputs/bundle/release/app-release.aab`

Alternatively, build an APK:

```bash
./gradlew assembleRelease
```

Output: `app/build/outputs/apk/release/app-release.apk`

---

## 2. Register at Samsung Seller Office

1. Go to [seller.samsungmobile.com](https://seller.samsungmobile.com).
2. Sign in with a Samsung account or create one.
3. Accept the developer agreement and complete registration (no fee).

---

## 3. Add your app in Seller Office

1. In the dashboard, choose **Add new application**.
2. **Application type:** Mobile app (phone/tablet).
3. **Upload:**  
   - Prefer **AAB** (`app-release.aab`) if the option is available.  
   - Otherwise upload the **APK** (`app-release.apk`).
4. Fill in:
   - **App name:** A Faith Driven Life
   - **Short description** (e.g. “Connect, share, and grow—blogs, resources, free study guides and books, audio, Bible search, and more.”)
   - **Full description:** What the app does (faith content, blog, resources, free books for kids and adults, study guides, audio, prayer requests, testimonies).
   - **Category:** e.g. Lifestyle or Education (choose the closest match).
   - **Content rating:** Complete the questionnaire (non-game, no paid features → usually low risk).
   - **Privacy policy URL:** Use your site’s privacy page if you have one, or a simple page on your GitHub Pages site.
5. **Graphics:**
   - **Icon:** 512×512 px (PNG).
   - **Screenshots:** At least one phone screenshot (e.g. home screen, blog list, resources). Optional: tablet screenshots.
6. Save and submit for review.

---

## 4. App content and policy

- **Free app:** Mark as free; no in-app purchases if you don’t have any.
- **Permissions:** The app uses **Internet** and optionally **Notifications** (for blog alerts). Galaxy Store will list these; no extra steps unless they ask.
- **Firebase:** If you use Firebase (Auth, FCM), ensure your app is configured correctly and that you’ve added any required data/privacy info in the store listing if requested.

---

## 5. After submission

- Review can take a few days. You’ll get status updates in Seller Office.
- If they request changes (screenshots, description, permissions, etc.), update the listing or build and resubmit.
- Once approved, the app will be available on the Galaxy Store for Samsung device users.

---

## Quick checklist

- [ ] Release AAB or APK built and signed
- [ ] Samsung Seller Office account created
- [ ] App uploaded (AAB or APK)
- [ ] Name, short and full description, category, and content rating filled
- [ ] 512×512 icon and at least one phone screenshot uploaded
- [ ] Privacy policy URL set (if required)
- [ ] App submitted for review

For the latest requirements and screens, always check the official [Samsung Galaxy Store developer pages](https://seller.samsungmobile.com) and their current submission guide.
