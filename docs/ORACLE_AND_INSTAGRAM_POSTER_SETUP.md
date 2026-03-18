# Step-by-step: Oracle Cloud – create your free Linux server

This guide gets you to a running Ubuntu server on Oracle Cloud (free tier) that you can log into with SSH. You can use it for any function later (e.g. posting to Instagram); that part is left for when you’re ready.

---

## Part 1: Oracle Cloud – create your free server

### Step 1.1 – Sign up

1. Go to **https://www.oracle.com/cloud/free/** and click **Start for free**.
2. Choose your country and click **Next**.
3. Enter your email and a password. Click **Create Account**.
4. Verify your email if asked.
5. You’ll be asked for **payment verification** (credit card). Oracle does **not** charge you as long as you use only **Always Free** resources. You can set a budget alert (e.g. $1) to be safe.
6. Complete identity verification (e.g. phone, address) if required.

### Step 1.2 – Create a VM instance

1. Log in to **https://cloud.oracle.com**.
2. In the top-left, open the **menu (≡)** → **Compute** → **Instances**.
3. Choose your **region** (e.g. your nearest). Click **Create Instance**.
4. **Name:** e.g. `my-server` (or any name you like).
5. **Placement:** leave default.
6. **Image and shape** (important for free tier). On screen you will see **Change Image** and **Change shape** (not "Edit").
   - **Image:** Click **Change Image**. In the Image dialog, pick **Canonical Ubuntu** and version **22.04** (so the OS is Ubuntu, not Oracle Linux 9).
   - **Shape:** Click **Change shape**. Select the Always free-eligible option, then **VM.Standard.E2.1.Micro** (1 OCPU, 1 GB memory). Click **Select shape**.
7. **Networking:** leave default (create new VCN if needed). Ensure **Assign a public IPv4 address** is checked.
8. **Add SSH keys:**
   - Choose **Generate a key pair for me**.
   - Click **Save private key** and **Save public key**. Store the private key somewhere safe. You’ll use it to log in.
9. Click **Create**.

Wait until the instance state is **Running** (green). Note the **Public IP address** (e.g. `123.45.67.89`).

### Step 1.3 – Open SSH port in the firewall

1. In the left menu: **Networking** → **Virtual cloud networks**.
2. Click your VCN (e.g. the one created with the instance).
3. Click your **Subnet** (e.g. “Public subnet-…”).
4. Click the **Default Security List**.
5. **Add Ingress Rule:**
   - Source: `0.0.0.0/0`
   - IP Protocol: TCP
   - Destination port: `22`
   - Click **Add Ingress Rules**.

### Step 1.4 – Log in to your server

From your computer (PowerShell or Terminal):

```bash
# Fix key permissions (Linux/Mac; on Windows use the path to your key)
chmod 600 /path/to/your-private-key.key

# Log in (replace with YOUR public IP and key path)
ssh -i /path/to/your-private-key.key ubuntu@YOUR_PUBLIC_IP
```

Example on Windows (if key is in your user folder):

```powershell
ssh -i $env:USERPROFILE\Downloads\your-private-key.key ubuntu@123.45.67.89
```

You should see a prompt like `ubuntu@my-server:~$`. **You’re on your Linux server.** The Oracle Linux server is successfully set up at this point. You can add other functions (e.g. posting to Instagram) on this server when you’re ready.
