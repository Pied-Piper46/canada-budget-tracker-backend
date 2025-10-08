#!/bin/bash

echo "Generating JWT secret key..."
JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

echo "Creating .env file..."
# Warning: change the env file name to your proper env before running this file
cat > .env.production << EOF
# JWT Configuration
JWT_SECRET_KEY=$JWT_SECRET

# Admin Password
ADMIN_PASSWORD=change_me_to_secure_password

# Plaid Configuration
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=your_plaid_env

# Database
DATABASE_URL=your_db_url
EOF

echo "✔︎ .env file created successfully!"
echo "⚠︎ Please update ADMIN_PASSWORD in .env file before runnign the app"
