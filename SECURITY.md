# Security Documentation

## Authentication & Authorization

### Overview
This application uses a multi-layered authentication system:
- **JWT (JSON Web Tokens)** via `djangorestframework-simplejwt` for API authentication
- **Email verification** for account activation
- **Custom authentication backend** supporting both email and username login
- **OAuth2** integration with Google for social authentication

### Authentication Flow

#### 1. User Registration
- Users register via `/api/auth/register/`
- Account is created with `is_active=False` by default
- Email verification token (JWT) is generated and sent to user's email
- Token expires in 24 hours

#### 2. Email Verification
- User clicks verification link in email
- Token is validated and user account is activated (`is_active=True`)
- JWT tokens are returned for immediate login

#### 3. Login
- Users can login via `/api/auth/login/` with either:
  - Email + Password
  - Username + Password
- Custom serializer checks if user is active before allowing login
- Returns access token (60 min) and refresh token (1 day)

#### 4. Token Refresh
- Access tokens expire after 60 minutes
- Refresh tokens can be used to obtain new access tokens
- Refresh tokens are rotated on use
- Old refresh tokens are blacklisted after rotation

#### 5. Logout
- Users send refresh token to `/api/auth/logout/`
- Token is blacklisted to prevent reuse

### Security Features Implemented

#### 1. Password Security
✅ Django's built-in password validators:
- UserAttributeSimilarityValidator
- MinimumLengthValidator (8 characters minimum)
- CommonPasswordValidator
- NumericPasswordValidator

✅ Passwords are hashed using Django's default PBKDF2 algorithm

#### 2. JWT Token Security
✅ Access tokens expire after 60 minutes
✅ Refresh tokens expire after 1 day
✅ Refresh token rotation enabled
✅ Token blacklisting enabled
✅ Tokens signed with SECRET_KEY using HS256 algorithm

#### 3. Email Verification
✅ Accounts inactive until email verified
✅ Verification tokens expire after 24 hours
✅ Tokens are JWT-based and cryptographically secure

#### 4. Environment Variable Security
✅ Secret keys stored in environment variables
✅ Database credentials in environment variables
✅ OAuth credentials in environment variables
✅ `.env.example` provided for reference

#### 5. HTTPS & Transport Security
✅ SSL redirect enforced in production
✅ Secure cookies in production
✅ HSTS enabled with 1-year duration
✅ Secure proxy headers configured

#### 6. Security Headers
✅ Content type nosniff enabled
✅ XSS filter enabled
✅ X-Frame-Options set to DENY
✅ CSRF protection enabled
✅ HTTP-only cookies for sessions

#### 7. Rate Limiting & Account Protection
⚠️ **Recommendation**: Consider implementing rate limiting
- Use `django-ratelimit` or `django-axes` for login attempt limiting
- Prevent brute force attacks on authentication endpoints
- Current settings: `ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5`

#### 8. User Enumeration Protection
✅ Resend verification endpoint returns same response regardless of email existence
✅ Prevents attackers from discovering valid email addresses

### Security Best Practices Followed

1. **Principle of Least Privilege**
   - Users start with minimal permissions
   - Admin permissions checked explicitly
   - Custom permissions for resource ownership

2. **Defense in Depth**
   - Multiple authentication methods
   - Token rotation and blacklisting
   - Email verification
   - Custom authentication backends

3. **Secure Defaults**
   - New users inactive by default
   - Debug mode from environment variable
   - Production security settings conditional on DEBUG=False

4. **Input Validation**
   - Django's built-in password validation
   - Serializer validation for all user inputs
   - Email format validation

### Potential Security Improvements

#### High Priority
1. **Implement Rate Limiting**
   ```bash
   pip install django-ratelimit
   ```
   Apply to:
   - Login endpoint
   - Registration endpoint
   - Password reset endpoint
   - Email verification resend

2. **Add CORS Configuration**
   ```bash
   pip install django-cors-headers
   ```
   Configure allowed origins properly

3. **Implement Account Lockout**
   ```bash
   pip install django-axes
   ```
   Lock accounts after multiple failed login attempts

#### Medium Priority
4. **Add 2FA Support**
   - Consider `django-otp` or `django-two-factor-auth`
   - Optional for users but recommended for admins

5. **Implement Content Security Policy (CSP)**
   ```bash
   pip install django-csp
   ```

6. **Add Security Monitoring**
   - Log failed authentication attempts
   - Monitor for suspicious patterns
   - Set up alerts for security events

7. **Regular Security Audits**
   - Keep dependencies updated
   - Run security scanners regularly
   - Review authentication logs

### API Endpoints Security Matrix

| Endpoint | Authentication | Authorization | Rate Limited |
|----------|---------------|---------------|--------------|
| `/api/auth/register/` | None | AllowAny | ⚠️ Recommended |
| `/api/auth/login/` | None | AllowAny | ⚠️ Recommended |
| `/api/auth/verify-email/` | None | AllowAny | ✅ Not needed |
| `/api/auth/resend-verification/` | None | AllowAny | ⚠️ Recommended |
| `/api/auth/logout/` | Required | IsAuthenticated | ✅ Not needed |
| `/api/auth/me/` | Required | IsAuthenticated | ✅ Not needed |
| `/api/auth/token/refresh/` | None (token) | AllowAny | ⚠️ Recommended |
| `/api/cart/*` | Required | IsAuthenticated | ✅ Not needed |
| `/api/products/*` | Optional | IsAuthenticatedOrReadOnly | ✅ Not needed |

### Common Attack Vectors & Mitigations

#### 1. Brute Force Attacks
- **Attack**: Automated password guessing
- **Mitigation**: Implement rate limiting (recommended)
- **Current**: Password complexity requirements

#### 2. Token Theft
- **Attack**: Stealing JWT tokens
- **Mitigation**: 
  - ✅ Short token lifetime (60 min)
  - ✅ Token rotation
  - ✅ HTTPS only cookies
  - ✅ HTTP-only cookies

#### 3. CSRF Attacks
- **Attack**: Forged requests from malicious sites
- **Mitigation**:
  - ✅ CSRF tokens enabled
  - ✅ SameSite cookies
  - ✅ JWT tokens in Authorization header

#### 4. XSS Attacks
- **Attack**: Injecting malicious scripts
- **Mitigation**:
  - ✅ Django's auto-escaping templates
  - ✅ Content-Type nosniff
  - ✅ XSS filter enabled
  - ✅ X-Frame-Options

#### 5. SQL Injection
- **Attack**: Malicious SQL queries
- **Mitigation**:
  - ✅ Django ORM parameterized queries
  - ✅ Input validation via serializers

#### 6. User Enumeration
- **Attack**: Discovering valid usernames/emails
- **Mitigation**:
  - ✅ Generic error messages
  - ✅ Same response for invalid emails

### OAuth Security

#### Google OAuth Configuration
- Configured in `SOCIALACCOUNT_PROVIDERS`
- Credentials stored in environment variables
- Auto-signup enabled for OAuth users
- Email verification skipped for OAuth (verified by provider)

### Logging & Monitoring

Current logging:
- Authentication events logged in `accounts.backends`
- Error logging for multiple users with same credentials

**Recommendations**:
1. Add structured logging
2. Log security events:
   - Failed login attempts
   - Password changes
   - Email verification
   - Token generation/validation
3. Set up monitoring alerts

### Environment Configuration

Required environment variables (see `.env.example`):
- `SECRET_KEY` - Django secret key (CRITICAL)
- `DEBUG` - Debug mode flag
- `ALLOWED_HOSTS` - Allowed host names
- `POSTGRES_*` - Database credentials
- `GOOGLE_CLIENT_*` - OAuth credentials
- `FRONTEND_URL` - Base URL for verification links

### Deployment Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` set
- [ ] Database credentials secured
- [ ] HTTPS enabled
- [ ] Security headers enabled
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Monitoring and logging set up
- [ ] Regular security updates scheduled
- [ ] Backup strategy in place

### Testing Security

Run security checks:
```bash
# Django security check
python manage.py check --deploy

# Check for vulnerable dependencies
pip install safety
safety check

# Run CodeQL or similar
# Configure in CI/CD pipeline
```

### Contact & Reporting

For security issues:
1. Do not open public issues
2. Contact maintainers directly
3. Provide detailed information
4. Allow time for patch before disclosure
