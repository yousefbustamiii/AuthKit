-- Clear data from leaf tables inward without dropping schema objects.
-- DELETE respects dependency order and avoids TRUNCATE's FK restrictions.

DELETE FROM sessions;
DELETE FROM trusted_devices;

DELETE FROM api_keys;
DELETE FROM invitations;
DELETE FROM organization_members;

DELETE FROM invoices;
DELETE FROM subscriptions;
DELETE FROM customers;

DELETE FROM projects;
DELETE FROM organizations;
DELETE FROM users;
