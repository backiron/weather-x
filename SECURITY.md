# Security Policy

## Supported version

Only the latest tagged release is supported.

## Reporting a vulnerability

Do not open a public issue containing a credential, private station location, or exploitable
deployment detail. Use the repository owner's private security-reporting channel.

## Secrets

Weather X does not require a built-in provider key. Keep optional provider credentials in local
environment variables or an external secret manager. Never commit `.env`, cookies, private keys,
database dumps, or raw authentication headers.

## Scope

This project is not designed for safety-critical, regulatory, high-impact, or emergency
operations.
