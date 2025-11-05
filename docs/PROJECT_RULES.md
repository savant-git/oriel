1.  No action may delete, rename, or alter essential files or libraries in a way that renders the system unusable. All edits must compile and run cleanly.

2.  Each script performs one solitary function. Complex behavior arises only through explicit composition of modules.

3.  Savant expands through shard hierarchies: Level 0–00 = atoms (words & characters) → Level 1 = snippets → Level 2 = scripts → Level 3+ = apps & systems.     Each level must remain modular, interoperable, and globally addressable. Levels 0–00 are global across all shard systems; higher levels are system-specific.

4.  All prose, documentation, and UI copy follow the Savant voice — meticulous, lucid, technical, and subtly poetic.

5.  These rules are binding unless formally superseded by the user.

6.  Explicit manual authorization overrides automation.

7.  Rollback, self-healing, and snapshot recovery daemons must remain active at all times.

8.  Every modification or extraction records a timestamped changelog in `/savant/logs/audit/`.

9.  Before and after major operations, full snapshots are versioned to S3 or equivalent local storage.

10. The project name *savant* always remains lowercase.

11. Vocabulary must follow canonical glossaries.

12. All outputs remain canon-consistent and context-aware.

13. Merge repetition into the most concise, lossless form.

14. Each major task passes through ten improvement cycles with ≥10 % measurable gain.

15. Lowest-confidence regions are re-optimized automatically.

16. Successful heuristics persist; failures refine future logic.

17. New rules emerge from logged failure patterns and carry UTC timestamps.

18. Only essential confirmations print; verbose logs redirect to files.

19. On uncertainty, halt safely and log the cause.

20. No infinite loops or uncaught exceptions.

21. Optimize only after baseline stability is confirmed.

22. Scripts import `rule_check`; execution halts if `PROJECT_RULES.md` is missing or outdated.

23. Every edit triggers a versioned backup.

24. Aliases, paths, and environment variables must remain synchronized across all host environments.

25. One shared AI client per environment; no duplicate keys.

26. AI checks directive timestamps before altering files.

27. Conversational and decision memory persist across sessions.

28. Every chat response **must**: - Begin with a unique reference header `[ #0001 ]`, incrementing per message. - Number each line below that header `1.`, `2.`, `3.` etc. - Maintain consistent indentation and spacing for clarity. - Follow the Savant voice and omit decorative or extraneous text. - Example: [#0001] 1. First line of reasoning. 2. Second line of reasoning. 3. Et cetera.

29. Gunmetal + gold palette, Inter / JetBrains Mono fonts, minimal motion, balanced spacing.

30. Visual output targets professional, award-level quality.

31. Every validated script auto-produces a ≥1000-word README in Savant voice.

32. All builds must distribute with the current `PROJECT_RULES.md`; its absence halts execution.

33. Rule files log diffs with UTC timestamps; they are never deleted — only superseded.

34. Enforcement logs include timestamp + path.

35. Continuous watcher repairs missing or corrupted files automatically.

36. Restore only affected files from the latest verified backup.

37. Background daemons restart within two minutes of failure.

38. Critical modules are write-protected; unauthorized edits trigger rollback.

39. Rolling checksums validate daemon health and logs.

40. Expose localhost-only, read-only endpoints for dashboards; forbid external network calls unless whitelisted.

41. Convert integrity JSON to lightweight visual summaries.

42. Maintain a verified system snapshot at `~/savant/integrity_cache/status.json`.

43. The latest uploaded archive defines the authoritative context.

44. Use `{App}_{mm-dd-yy}_{ver}.zip`.

45. Each archive includes `App_manifest.json` with metadata and environment notes.

46. Push after scaffold completion or any major change with full source + manifest + README.

47. Prefer newest date, then highest semantic version.

48. New apps adopt prior stack conventions and hygiene.

49. Automated verification restores missing or corrupt files from backup.

50. Monitors every service and triggers auto-repair on unauthorized edits.

51. Recovers specific files, not whole directories.

52. System and Python libraries are excluded from cleanups.

53. Watcher writes concise logs for UI display.

54. All structural changes must include rationale and scope notes.

55. Precision precedes decoration.

56. Elegance is earned through structure and restraint.

57. Each iteration refines toward truth, function, and elegance.
