# Hello World

This is obviously not my first GitHub repository!

## About Me
I'm a software engineer at SEECS, NUST, learning GitHub and AI-powered development.

## Module 1

- Learned about GitHub codespaces!

- And discovered that it works with VSCode Live Share, although, I don't use that extension much when working in teams. (except when I have to work in a pair programming setup)

![codespaces image](images/codespaces.png)

- This will surely help boost productivity

- I never knew that VSCode auto-complete suggestions can be used in so many different ways!

![autocomplete image](images/autocomplete.png)

- Used co-pilot as usual to generate documentation for the task manager created in module_1 lab.

![prompting image](images/prompting.png)

- Created a task Manager using just autocomplete and code comments

![task manager image](images/task_manager.png)

- Added unittests for the task manager (like i always do)

![unittests task manager](images/unittests_task_manager.png)

---

## Module 2

- Learned a lot of useful shortcut keys for using co-pilot suggestions!

- The /explain feature can be quite handy when dealing with other people's code:

![unittests task manager](images/explain_copilot.png)

- The /fix feature can also be very handy:

![fix feature image](images/fix.png)

- Same goes for the /rewrite feature

- **Reflection on exercise 1 of unit 2**

Use of different modes for different tasks is quite interesting plus useful. I personally prefer using ChatGPT for the "ask" mode, generally, to save premium copilot requests.

However, the "edit" mode is actually useful when we already have the implementation and just need some quick edits for improvements, and I would use that mode from now on. 

- **Reflection on exercise 2 of unit 2**

Python - Uses a tuple that returns the success message, regex for email validation. It could raise exceptions in case of errors.

Javascript - Uses async/await and throws errors for validation failures. Uses regex patterns, and try/catch blocks to handle errors.

Typescript - Uses type annotations and interfaces, uses type safety instead of tuples and for error handling, it should throw an error or return a `Result` type.

- Python generators? js question, Docker?? optimizing SQL queries??

Python generators: Functions using yield that produce values lazily one at a time, saving memory; use for large datasets or infinite sequences.

var, let, const in JavaScript: var is function-scoped and hoisted, let is block-scoped and reassignable, const is block-scoped and immutable reference.

Docker purpose: Containerization platform that packages applications with dependencies into isolated containers using OS-level virtualization for consistent deployment.

SQL query optimization: Use indexes, avoid SELECT *, limit result sets, optimize JOINs, partition tables, use query execution plans, and cache frequently accessed data.

- Best way to implement caching?

For the user registration system, the best caching approach would be:

Cache user lookups by email and ID (most frequent operations)
Use TTL (Time-To-Live) to prevent stale data
Implement cache-aside pattern - check cache first, then database
LRU eviction for memory management
Cache invalidation on user updates/deletions
Thread-safe operations for concurrent access


- How do I test caching?

To test caching behavior effectively, you should:

Test cache hits and misses - Verify data is cached on first access and retrieved from cache on subsequent calls
Test TTL expiration - Ensure cached data expires after the configured time
Test cache invalidation - Confirm cache clears when data is updated/deleted
Test LRU eviction - Verify old entries are evicted when cache is full
Test thread safety - Ensure concurrent access works correctly
Measure cache performance - Verify hit rate and response time improvements
Test cache statistics - Validate metrics are tracked correctly


- For the full-stack lab, the tasks were quite interesting. I have put that system in `module_2/task_management_system/`

- As for the questions, I have answered them in REFLECTION.md in the same directory.

---

## Module 3

- Learned and used some more slash commands. `/doc` is really useful for doing the tiring work of adding documentation, however, the doc LLMs generate still has to be reviewed by a human.

![slash doc usage image]('images/slash_doc_example.png')

- 