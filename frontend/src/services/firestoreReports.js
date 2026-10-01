import {
  addDoc,
  collection,
  deleteDoc,
  doc,
  getDocs,
  orderBy,
  query,
  where,
} from "firebase/firestore";
import { db } from "../lib/firebase";

const reportsCollection = collection(db, "reports");

export async function saveReport(report, userId) {
  const reportData = {
    ...report,
    userId,
    createdAt: new Date().toISOString(),
  };

  const docRef = await addDoc(reportsCollection, reportData);

  return {
    id: docRef.id,
    ...reportData,
  };
}

export async function getUserReports(userId) {
  const q = query(
    reportsCollection,
    where("userId", "==", userId),
    orderBy("createdAt", "desc"),
  );

  const snapshot = await getDocs(q);

  return snapshot.docs.map((doc) => ({
    id: doc.id,
    ...doc.data(),
  }));
}

export async function deleteReport(reportId) {
  await deleteDoc(doc(db, "reports", reportId));
}