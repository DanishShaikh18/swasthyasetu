import { openDB } from 'idb'

const DB_NAME = 'swasthyasetu-offline'
const DB_VERSION = 1

async function getDB() {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains('profile')) db.createObjectStore('profile')
      if (!db.objectStoreNames.contains('prescriptions')) db.createObjectStore('prescriptions')
      if (!db.objectStoreNames.contains('firstAid')) db.createObjectStore('firstAid')
      if (!db.objectStoreNames.contains('dailyTip')) db.createObjectStore('dailyTip')
    },
  })
}

export async function saveOffline(store, key, data) {
  const db = await getDB()
  await db.put(store, data, key)
}

export async function getOffline(store, key) {
  const db = await getDB()
  return db.get(store, key)
}

export async function getAllOffline(store) {
  const db = await getDB()
  return db.getAll(store)
}
