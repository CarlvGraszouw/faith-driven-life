/**
 * Firebase Cloud Functions for A Faith Driven Life app.
 * newBlogCheck: runs every 6 hours, checks Blogger feed, sends FCM to "new_blog" topic if there is a new post.
 */

const { onSchedule } = require("firebase-functions/v2/scheduler");
const admin = require("firebase-admin");

admin.initializeApp();

const BLOGGER_FEED_URL =
  "https://awfgsa.blogspot.com/feeds/posts/default?alt=json&max-results=1";
const SITE_BLOGS_URL = "https://carlvgraszouw.github.io/faith-driven-life/blogs.html";

async function getLatestPost() {
  const res = await fetch(BLOGGER_FEED_URL);
  if (!res.ok) return null;
  const data = await res.json();
  const entry = data?.feed?.entry?.[0];
  if (!entry) return null;
  const link = entry.link?.find((l) => l.rel === "alternate")?.href || SITE_BLOGS_URL;
  return {
    id: entry.id?.$t || entry.id,
    title: entry.title?.$t || "New post",
    updated: entry.updated?.$t || "",
    link,
  };
}

const DB_COLLECTION = "blog_notifications";
const DB_DOC = "last_post";

async function getLastNotifiedId() {
  const doc = await admin.firestore().collection(DB_COLLECTION).doc(DB_DOC).get();
  return doc.exists ? doc.data().postId : null;
}

async function setLastNotifiedId(postId) {
  await admin.firestore().collection(DB_COLLECTION).doc(DB_DOC).set({
    postId,
    updatedAt: admin.firestore.FieldValue.serverTimestamp(),
  });
}

exports.newBlogCheck = onSchedule(
  { schedule: "every 6 hours", timeoutSeconds: 60, memory: "256MiB" },
  async () => {
    const latest = await getLatestPost();
    if (!latest) {
      console.log("Could not fetch Blogger feed");
      return;
    }
    const lastId = await getLastNotifiedId();
    if (lastId === latest.id) {
      console.log("No new post since last check");
      return;
    }
    await setLastNotifiedId(latest.id);
    const message = {
      notification: { title: "A Faith Driven Life", body: latest.title },
      data: { url: latest.link },
      topic: "new_blog",
    };
    await admin.messaging().send(message);
    console.log("Sent new_blog notification for:", latest.id);
  }
);
