/**
 * auth_guard.ts
 * Enforces non-negotiable rules before any mutation.
 */

export function enforceRules(directives: Record<string, any>): void {
  const rules = directives?.rules || {};
  if (!rules) throw new Error("No rules found in directives.");

  if (!rules.single_source_of_truth)
    throw new Error("Directive violation :: single_source_of_truth missing.");

  console.log("✔ Auth Guard :: rules validated");
}
