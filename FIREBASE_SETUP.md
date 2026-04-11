# 🔧 Firebase Setup Instructions

## Step 1: Set Database Rules

Go to: **Firebase Console** → `med-phone-e4814` → **Realtime Database** → **Rules**

Paste this and click **Publish**:

```json
{
  "rules": {
    "commandes": {
      ".read": true,
      ".write": true
    },
    "products": {
      ".read": true,
      ".write": true
    },
    ".read": "auth != null",
    ".write": "auth != null"
  }
}
```

## Step 2: Deploy

```bash
firebase deploy
```

## Step 3: Test

1. Add product to cart → Payment → fill form → Place Order
2. Go to `Admin.html` → password: **MedAdmin2026!** → see your orders

## Admin Panel

- **URL:** `https://med-phone-e4814.web.app/Admin.html`
- **Password:** `MedAdmin2026!`
