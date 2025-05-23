# JusPrin Server Setup Guide

## Overview

This guide provides instructions for setting up a self-hosted server for the [JusPrin client](https://github.com/TheSpaghettiDetective/JusPrin).

**JusPrin is fully open source**—not only to empower makers and developers, but also to serve as a real-world learning resource for those interested in **how Generative AI can power practical applications**.

---

## JusPrin Server Architecture

1. The JusPrin backend is currently integrated into the **Obico server**.
2. To self-host JusPrin, follow the [Obico server setup documentation](https://www.obico.io/docs/server-guides/).
3. Once the server is running, you’ll need to configure an OAuth App to allow secure access for your JusPrin client.

---

## Setting Up an OAuth App for JusPrin

Once your Obico server is up and running, follow these steps to register an OAuth application for JusPrin:

1. Log in to your Obico server's admin interface, e.g., `http://your_server_ip:3334/admin/`.
2. Go to the **OAuth Applications** section (typically found under: Home › OAuth2_Provider › Applications).
3. Click **“Add application”** to create a new entry.
4. Fill in the fields as follows:

   - **Client id**: `JusPrin`
   - **User**: Select your admin user (e.g., `1 - root@example.com`)
   - **Redirect URIs**: Add your authorized redirect URI, e.g., `http://your_server_ip:3334/orca_slicer/authorized/`.
     - You may include multiple URIs separated by spaces.
     - Replace this with your domain in production.
   - **Client type**: `Public`
   - **Authorization grant type**: `Implicit`
   - **Client secret**: (Auto-generated)
   - **Name**: `JusPrin`
   - **Skip authorization**: ✅ Check this box
   - **Algorithm**: `None` (OIDC not supported)

5. Click **Save** to create the application.

---

## Client Configuration

After setting up the OAuth app, open JusPrin client's settings dialog, and update JusPrin server configuration to:

- Your server’s base URL, e.g., `http://your_server_ip:3334/`

---

## Troubleshooting

If you run into issues during setup:

- ✅ Confirm your Obico server is configured and running.
- ✅ Double-check your OAuth app’s redirect URIs.
- ✅ Inspect server logs for authentication or connection errors.

For more help, check out:

- 📚 [Obico Documentation](https://www.obico.io/docs/)
- 💬 [Join our Discord](https://discord.gg/Tx67dHNYH3) to connect with the developer and maker community.

---

By open-sourcing JusPrin, we hope it can also serve as a **learning playground** for developers, students, and AI enthusiasts who want to explore how Generative AI can be integrated into real-world software.

Happy building! 🧠🔧
