# Authentication decision scenarios

Use the relevant case when reviewing a design or testing whether this skill changes an agent's decisions. These are acceptance examples, not extra runtime steps.

## New consumer application

Request: add accounts to save private projects across devices; no existing provider preference.

Expected: ordinary-account profile, maintained authentication library/provider, passkey-first enrollment/login with required verification, independent backup and viable recovery, revocable sessions, and a short app-specific contract. Choose an implementation that fits the stack. Do not add an identity service merely to standardize policy.

## Existing password users

Request: add passkeys to an app with working password/TOTP login and recovery codes.

Expected: preserve existing access, use fresh password plus TOTP for first-passkey enrollment where that is the current approved method, test backup/recovery, and migrate incrementally. Password plus a saved backup code is a second-factor authentication path: record its method and apply the action policy rather than silently treating it as account replacement. Passkey verification requires UV on the server; adding another TOTP prompt after it is not the default. Do not remove existing credentials on enrollment.

## Recovered attacker enrolls a passkey

Request: email-only recovery issues a restricted session; a newly enrolled passkey signs in successfully. May it replace payout destinations or grant an administrator role?

Expected: enforce the recorded restrictions and capability-specific strength/provenance requirements. New key enrollment and a successful assertion do not promote recovery trust. Define independent proof or operator recovery for these protected actions. For all-proof-loss ordinary access, implement the product-selected delayed mailbox path or independent arrangement, or disclose the unrecoverable loss condition during setup. A timer cannot manufacture independent proof. Verify cancellation and its effect on newly enrolled credentials.

## Privileged operator loses every key

Request: the only enabled operator has lost both keys. Email works, and a cross-platform passkey response has no trusted attestation.

Expected: use a pre-established infrastructure trust root or independent operator approval, bind hardware-key enrollment to that procedure, and require the documented delay, audit, and notifications. Before privileges resume, verify two independent approved keys. Missing attestation requires the documented controlled-inventory enrollment procedure or a blocker. Neither email control nor attachment type proves approved hardware. Explain a missing recovery arrangement as a blocker instead of inventing it.

## Offline encrypted notebook

Request: standardize auth for a local notebook with encrypted files and no sync.

Expected: keep no-account operation, use supported OS verification and vault key recovery, and check offline restore. A WebAuthn assertion or web-account reset cannot recover the data key.

## Provider and agent identity

Request: a logged-in provider user and an MCP client have the same email as the owner. Let them change organization membership.

Expected: resolve immutable provider subject separately from app membership; check the current human's privilege and fresh assurance. A delegated grant cannot link identities, expand itself, or become an interactive human session because an email matches. Verify equivalent denial through all affected adapters.

## Compromised last credential

Request: revoke the only credential, or one of a privileged operator's two keys, after theft. The requester has an existing authenticated session.

Expected: the existing session may revoke its own establishing credential without freshness, ending all sessions/grants derived from it; revoking another credential needs a remaining fresh factor, recovery proof, or the trust root. Revoke the affected authority and enter recovery or suspend privileged capabilities. A remaining approved key may authorize maintenance-only replacement enrollment; an anonymous report cannot revoke credentials. An ordinary removal guard cannot preserve a compromised credential merely to avoid lockout.

## Recovery request used for denial of service

Request: someone submits an account's email to start recovery while its owner is signed in.

Expected: rate-limit and notify without ending the owner's session. Stronger verified compromise proof may suspend affected authority under the documented contract. Complete/promote recovery atomically, invalidate the old authority then, and let pre-existing proof cancel the pending flow without granting access.
