"""
Mock Regulatory Documents
Sample PCI-DSS, GDPR, CCPA, and internal policy text
"""

PCI_DSS_MOCK = """
PCI DSS v4.0 - Payment Card Industry Data Security Standard

Requirement 3: Protect Stored Cardholder Data

3.1 Processes and mechanisms for protecting stored account data are defined and understood.

3.2 Storage of account data is kept to a minimum.

3.2.1 Account data storage is kept to a minimum through implementation of data retention and disposal policies, procedures, and processes.

Primary Account Number (PAN) must not be stored or transmitted in plaintext in logs, support tickets, customer communications, or any unencrypted format. When PAN must be displayed, render unreadable through masking (showing only the first six and last four digits is acceptable).

3.3 Sensitive authentication data (SAD) is not stored after authorization.

Card Verification Value (CVV, CVV2, CVC) must not be stored under any circumstances after transaction authorization. This includes storage in logs, databases, support systems, or backup media.

3.4 Primary Account Number (PAN) is secured wherever it is stored.

PAN must be rendered unreadable anywhere it is stored (including portable digital media, backup media, in logs) by using one of the following approaches:
- Strong cryptography with associated key-management processes and procedures
- Truncation (hashing cannot be used to replace the truncated segment of PAN)
- Index tokens and pads (pads must be securely stored)
- Strong cryptography with associated key-management processes

Requirement 4: Protect Cardholder Data with Strong Cryptography During Transmission Over Open, Public Networks

4.1 Processes and mechanisms for protecting cardholder data with strong cryptography during transmission over open, public networks are defined and documented.

4.2 PAN is protected with strong cryptography whenever it is transmitted or sent via end user messaging technologies.

Never send unprotected PANs by end-user messaging technologies (e.g., e-mail, instant messaging, SMS, chat). Implement strong cryptography for transmission and display (e.g., TLS, SFTP, end-to-end encryption).

Requirement 8: Identify Users and Authenticate Access to System Components

8.2 User identification and related accounts for users and administrators are strictly managed.

8.2.1 User password/passphrase must meet minimum length of 7 characters (or 12 for system/application passwords) and contain both numeric and alphabetic characters.

8.3 Multi-factor authentication (MFA) is implemented for all access to the cardholder data environment (CDE).

Requirement 10: Log and Monitor All Access to System Components and Cardholder Data

10.2 Audit logs are implemented to support the detection of anomalies and suspicious activity.

All access to cardholder data must be logged with user identification, type of event, date and time, success or failure indication. Logs must not contain full PAN or sensitive authentication data.

10.3 Audit logs are protected from destruction and unauthorized modifications.

Requirement 12: Support Information Security with Organizational Policies and Programs

12.1 A comprehensive information security policy is established, published, maintained, and disseminated to all personnel.

12.5 PCI DSS scope is documented and validated annually.

Security policies must be reviewed at least annually and updated as needed to reflect changes to business objectives or the risk environment.
"""

GDPR_MOCK = """
REGULATION (EU) 2016/679 - General Data Protection Regulation (GDPR)

CHAPTER I - GENERAL PROVISIONS

Article 4 - Definitions

For the purposes of this Regulation:
(1) 'personal data' means any information relating to an identified or identifiable natural person ('data subject'); an identifiable natural person is one who can be identified, directly or indirectly, in particular by reference to an identifier such as a name, an identification number, location data, an online identifier.

Article 5 - Principles relating to processing of personal data

(1) Personal data shall be:
(a) processed lawfully, fairly and in a transparent manner in relation to the data subject ('lawfulness, fairness and transparency');
(b) collected for specified, explicit and legitimate purposes and not further processed in a manner that is incompatible with those purposes ('purpose limitation');
(c) adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed ('data minimisation');
(d) accurate and, where necessary, kept up to date ('accuracy');
(e) kept in a form which permits identification of data subjects for no longer than is necessary for the purposes for which the personal data are processed ('storage limitation');

Personal data shall be kept in a form which permits identification of data subjects for no longer than is necessary. Data retention policies must be implemented and enforced.

CHAPTER III - RIGHTS OF THE DATA SUBJECT

Article 17 - Right to erasure ('right to be forgotten')

(1) The data subject shall have the right to obtain from the controller the erasure of personal data concerning him or her without undue delay and the controller shall have the obligation to erase personal data without undue delay.

Individuals have the right to request deletion of their personal information. Organizations must have processes in place to honor such requests within one month.

CHAPTER IV - CONTROLLER AND PROCESSOR

Article 25 - Data protection by design and by default

(1) The controller shall implement appropriate technical and organisational measures for ensuring that, by default, only personal data which are necessary for each specific purpose of the processing are processed.

Privacy-by-design principles must be implemented: data minimization, pseudonymization, encryption, and access controls must be default configurations.

Article 32 - Security of processing

(1) The controller and processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk, including:
(a) the pseudonymisation and encryption of personal data;
(b) the ability to ensure the ongoing confidentiality, integrity, availability and resilience of processing systems;
(c) regular testing, assessing and evaluating effectiveness of security measures.

Personal data must be encrypted in transit and at rest. Access controls must be implemented. Regular security assessments are required.

Personal identifiers including email addresses, phone numbers, and IP addresses are considered personal data under GDPR. These identifiers should not be stored in application logs in plaintext without a legitimate processing basis and appropriate safeguards. When logging is necessary for security or debugging purposes, personal identifiers must be pseudonymized, hashed, or masked to protect individual privacy.

Article 33 - Notification of a personal data breach to the supervisory authority

(1) In the case of a personal data breach, the controller shall without undue delay and, where feasible, not later than 72 hours after having become aware of it, notify the personal data breach to the supervisory authority.

Personal data breaches must be reported to the supervisory authority within 72 hours. Notification must include nature of breach, categories of data, likely consequences, and measures taken.

Article 35 - Data protection impact assessment

(1) Where a type of processing is likely to result in a high risk to the rights and freedoms of natural persons, the controller shall carry out an assessment of the impact of the processing operations on the protection of personal data.

Data Protection Impact Assessments (DPIAs) must be conducted for high-risk processing activities involving sensitive data or systematic monitoring.
"""

CCPA_MOCK = """
California Consumer Privacy Act of 2018 (CCPA)

CIVIL CODE - CIV
DIVISION 3. OBLIGATIONS
PART 4. OBLIGATIONS ARISING FROM PARTICULAR TRANSACTIONS
TITLE 1.81.5. California Consumer Privacy Act of 2018

§ 1798.100. Consumer Rights - Right to Know

(a) A consumer shall have the right to request that a business that collects a consumer's personal information disclose to that consumer the categories and specific pieces of personal information the business has collected.

Businesses must disclose what personal information has been collected, the categories of sources, business purpose for collection, and categories of third parties with whom information is shared.

(b) A business that collects a consumer's personal information shall, at or before the point of collection, inform consumers of the categories of personal information to be collected and the purposes for which the categories of personal information shall be used.

Consumers have the right to know what personal information is collected about them and how it will be used. Clear notice must be provided at or before collection.

§ 1798.105. Consumer Rights - Right to Delete

(a) A consumer shall have the right to request that a business delete any personal information about the consumer which the business has collected from the consumer.

(b) A business that receives a verifiable consumer request to delete shall delete the consumer's personal information from its records and direct any service providers to delete the consumer's personal information.

Consumers have the right to request deletion of their personal information. Businesses must honor deletion requests within 45 days (extendable to 90 days with notice).

§ 1798.110. Consumer Rights - Access to Specific Information

A consumer shall have the right to request that a business that collects personal information about the consumer disclose the specific pieces of personal information it has collected about that consumer.

§ 1798.115. Consumer Rights - Right to Know About Information Sold or Disclosed

(a) A consumer shall have the right to request that a business that sells the consumer's personal information, or that discloses it for a business purpose, disclose to that consumer:
(1) The categories of personal information that the business collected about the consumer.
(2) The categories of personal information that the business sold about the consumer and the categories of third parties to whom the personal information was sold.

§ 1798.120. Right to Opt-Out of Sale of Personal Information

(a) A consumer shall have the right, at any time, to direct a business that sells personal information about the consumer to third parties not to sell the consumer's personal information. This right is referred to as the right to opt-out.

Consumers must be able to opt out of the sale of their personal information. A clear "Do Not Sell My Personal Information" link must be provided on the homepage.

§ 1798.150. Security Requirements and Private Right of Action

Businesses must implement and maintain reasonable security procedures and practices appropriate to the nature of the personal information to protect the personal information from unauthorized access, destruction, use, modification, or disclosure.
"""

INTERNAL_POLICY_MOCK = """
COMPANY DATA PROTECTION AND PRIVACY POLICY
Version 2024.1
Effective Date: January 1, 2024

1. DATA CLASSIFICATION AND HANDLING

1.1 Data Classification Levels

All company data must be classified into one of four categories:
- PUBLIC: Information intended for public distribution
- INTERNAL: Information for internal use only
- CONFIDENTIAL: Sensitive business information
- RESTRICTED: Highly sensitive data (PII, PAN, credentials)

1.2 Payment Card Data Handling

Primary Account Numbers (PAN) and Card Verification Values (CVV) are classified as RESTRICTED.

PAN must never appear in:
- Application logs
- Customer support chat transcripts
- Email communications
- Unencrypted databases
- System monitoring dashboards

When PAN must be displayed for legitimate business purposes, only the last 4 digits may be shown. Full PAN must be masked as: ****-****-****-1234

1.3 Personal Identifiable Information (PII) Handling

Personal identifiers including email addresses, phone numbers, social security numbers, and IP addresses are classified as CONFIDENTIAL or RESTRICTED depending on context.

Phone numbers, email addresses, and other PII should not be stored in application logs without explicit business justification and appropriate controls. When logging is necessary for debugging or security purposes:
- Personal identifiers must be masked or hashed
- Logs containing PII must be encrypted
- Access to such logs must be restricted and audited
- Retention period must be minimized (maximum 90 days unless legally required)

Best practice: Use tokenization or pseudonymization for customer identifiers in logs rather than actual phone numbers or email addresses.

2. DATA RETENTION AND DELETION

2.1 Customer Data Retention Policy

Customer personal data must not be retained longer than 24 months unless:
- Required by law or regulation
- Explicitly consented to by customer
- Necessary for ongoing service delivery

2.2 Automated Deletion

Automated data deletion jobs must run monthly to purge:
- Customer support chat logs older than 24 months
- Transaction logs containing PII older than 36 months
- Marketing data for unsubscribed users older than 12 months

3. ACCESS CONTROL AND MONITORING

3.1 Multi-Factor Authentication (MFA)

All access to systems containing RESTRICTED data must require:
- Username and strong password (minimum 12 characters)
- Multi-factor authentication via authenticator app or hardware token

3.2 Access Logging

All access to RESTRICTED data must be logged with:
- User identity
- Timestamp (UTC)
- Action performed (read, write, delete)
- IP address and device identifier

Access logs must be retained for 7 years and reviewed quarterly.

4. ENCRYPTION STANDARDS

4.1 Data at Rest

All RESTRICTED data must be encrypted at rest using:
- AES-256 encryption
- Industry-standard key management
- Regular key rotation (every 180 days)

4.2 Data in Transit

All transmission of RESTRICTED data must use:
- TLS 1.2 or higher
- Perfect forward secrecy
- Certificate pinning where applicable

5. INCIDENT RESPONSE

5.1 Data Breach Notification

In the event of unauthorized access to RESTRICTED data:
- Security team must be notified within 1 hour
- Incident response plan activated within 2 hours
- Executive leadership notified within 4 hours
- Regulatory notification (if required) within 72 hours
- Customer notification (if required) within 7 days

5.2 Breach Investigation

All data breaches must be investigated to determine:
- Scope of data exposure
- Root cause analysis
- Affected customers or systems
- Remediation actions required

6. EMPLOYEE TRAINING

6.1 Mandatory Security Training

All employees must complete:
- Annual data protection training
- Role-specific compliance training
- Incident response drills

6.2 Developers and Engineers

Engineering staff must complete additional training on:
- Secure coding practices
- PCI-DSS requirements for developers
- Privacy-by-design principles

7. VENDOR AND THIRD-PARTY MANAGEMENT

7.1 Third-Party Data Sharing

Before sharing RESTRICTED data with third parties:
- Data Processing Agreement must be executed
- Security assessment must be completed
- Access must be logged and monitored

8. COMPLIANCE MONITORING

8.1 Automated Compliance Scanning

Automated tools must scan for compliance violations:
- Daily scans of application logs for PAN/CVV patterns
- Weekly scans of databases for unencrypted RESTRICTED data
- Monthly code repository scans for hardcoded credentials

8.2 Manual Audits

Quarterly manual audits must review:
- Access logs for anomalous behavior
- Data retention compliance
- Vendor compliance with DPAs
- Effectiveness of encryption controls

9. POLICY GOVERNANCE

This policy must be:
- Reviewed annually by Legal, Security, and Compliance teams
- Updated within 30 days of regulatory changes
- Acknowledged by all employees annually
- Enforced through automated controls and manual oversight

Violations of this policy may result in disciplinary action up to and including termination.

Document Owner: Chief Information Security Officer (CISO)
Last Reviewed: January 1, 2024
Next Review Due: January 1, 2025
"""
