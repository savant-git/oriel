/**
 * directive_enforcer.ts
 * Minimal rule validator for manifest and directives.
 */
export function enforceRules(directives: any): void {
  if (!directives) throw new Error("No directives or manifest provided.");
  if (!directives.apps)
    throw new Error("Manifest missing 'apps' section.");

  console.log("✔ Directive enforcement passed");
}
