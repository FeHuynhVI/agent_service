"""Prompt templates for subject expert tasks."""

CS_WRITE_CODE_PROMPT = """
Write {language} code to solve:
{problem}

Include:
1. Problem analysis
2. Algorithm explanation
3. Complete, working code
4. Time/space complexity analysis
5. Test cases
6. Possible optimizations
"""

CS_DEBUG_CODE_PROMPT = """
Debug the following code:
```
{code}
```
Error message: {error}

Provide:
1. Error identification
2. Root cause analysis
3. Fixed code
4. Explanation of changes
5. Prevention tips
"""

CS_EXPLAIN_ALGORITHM_PROMPT = """
Explain the {algorithm} algorithm:

Include:
1. Concept and purpose
2. Step-by-step process
3. Pseudocode
4. Implementation example
5. Time and space complexity
6. Use cases
7. Advantages and limitations
"""

MATH_SOLVE_PROBLEM_PROMPT = """
Solve the following math problem:
{problem}

Provide:
1. Restatement of the problem
2. Step-by-step solution with reasoning
3. Final answer
4. Verification of the result
"""

PHYSICS_SOLVE_PROBLEM_PROMPT = """
Solve the following physics problem:
{problem}

Instructions:
1. Restate the problem concisely
2. Identify the physical quantities and laws involved
3. Draw or describe diagrams if helpful
4. Write down relevant equations
5. Solve algebraically, showing each step
6. Plug in numerical values with appropriate units
7. Provide the final numerical answer with units
8. Comment on the physical interpretation of the result
"""

PHYSICS_EXPLAIN_CONCEPT_PROMPT = """
Explain the following physics concept:
{concept}

Include in your explanation:
1. A definition and the fundamental principles underlying the concept
2. Key equations and how they are derived
3. Example problems or scenarios that illustrate the concept
4. Visual or descriptive representation (what diagrams would show)
5. Applications in everyday life or technology
6. Common misconceptions or pitfalls
"""

CHEM_BALANCE_EQUATION_PROMPT = """
Balance the following chemical equation:
{equation}

Show the step-by-step process and explain the method used.
If it's a redox reaction, show the half-reactions.
"""

CHEM_PREDICT_REACTION_PROMPT = """
Predict the products of the following reaction:
Reactants: {reactants}
Conditions: {conditions}

Include:
1. Predicted products
2. Reaction mechanism (if applicable)
3. Reasoning for the prediction
4. Possible side products
"""

BIOLOGY_EXPLAIN_CONCEPT_PROMPT = """
Explain the following biology concept:
{concept}

Include:
1. Definition
2. Key processes or structures involved
3. Real-world examples or applications
4. Common misconceptions
"""

ENGLISH_CORRECT_GRAMMAR_PROMPT = """
Correct the following sentence for grammatical errors and explain each correction:

"{sentence}"

Provide:
1. The corrected sentence
2. A breakdown of each error and the corresponding rule
3. Suggestions for how to avoid similar mistakes in the future
"""

ENGLISH_BUILD_VOCABULARY_PROMPT = """
Teach the word "{word}" in detail.

Include:
1. Definition and part of speech
2. Pronunciation with phonetic transcription
3. Synonyms and antonyms
4. Example sentences demonstrating correct usage
5. Common collocations or phrases with the word
6. Etymology or origin (if interesting)
"""

LIT_ANALYZE_TEXT_PROMPT = (
    "Analyze the following text:\n\n"
    "{text}\n\n"
    "{question_part}Provide:\n"
    "1. A brief summary of the text\n"
    "2. Identification of themes, symbols and stylistic devices\n"
    "3. Analysis of character development and narrative perspective\n"
    "4. Discussion of the historical and cultural context\n"
    "5. Connections to other works or genres\n"
    "6. Your interpretation and critical viewpoint"
)

LIT_GIVE_WRITING_ADVICE_PROMPT = """
Provide guidance for the following writing assignment:
{assignment}

Your advice should include:
1. Interpretation of the assignment requirements
2. Suggestions for outlining and structuring the response
3. Tips on developing a clear thesis and supporting arguments
4. Advice on style, tone and voice appropriate to the genre
5. Common pitfalls to avoid
6. Recommendations for revision and editing
"""

__all__ = [
    "CS_WRITE_CODE_PROMPT",
    "CS_DEBUG_CODE_PROMPT",
    "CS_EXPLAIN_ALGORITHM_PROMPT",
    "MATH_SOLVE_PROBLEM_PROMPT",
    "PHYSICS_SOLVE_PROBLEM_PROMPT",
    "PHYSICS_EXPLAIN_CONCEPT_PROMPT",
    "CHEM_BALANCE_EQUATION_PROMPT",
    "CHEM_PREDICT_REACTION_PROMPT",
    "BIOLOGY_EXPLAIN_CONCEPT_PROMPT",
    "ENGLISH_CORRECT_GRAMMAR_PROMPT",
    "ENGLISH_BUILD_VOCABULARY_PROMPT",
    "LIT_ANALYZE_TEXT_PROMPT",
    "LIT_GIVE_WRITING_ADVICE_PROMPT",
]
