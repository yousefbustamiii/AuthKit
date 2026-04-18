export function generate_idempotency_key(): string {
  return crypto.randomUUID()
}
