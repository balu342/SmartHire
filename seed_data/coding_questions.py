CODING_QUESTIONS = [

    {
        "title": "Two Sum",
        "description": "Given an array of integers and a target, find the indices of two numbers whose sum equals the target.",
        "difficulty": "Easy",
        "category": "Arrays",
        "input_format": "First line: space-separated integers. Second line: target.",
        "output_format": "Print the two indices.",
        "sample_input": "2 7 11 15\n9",
        "sample_output": "0 1",
        "constraints": "2 <= array length <= 10000"
    },
    {
        "title": "Maximum Subarray Sum",
        "description": "Find the maximum sum of a contiguous subarray.",
        "difficulty": "Medium",
        "category": "Arrays",
        "input_format": "First line: N. Second line: N integers.",
        "output_format": "Print maximum subarray sum.",
        "sample_input": "9\n-2 1 -3 4 -1 2 1 -5 4",
        "sample_output": "6",
        "constraints": "1 <= N <= 100000"
    },
    {
        "title": "Rotate Array",
        "description": "Rotate an array to the right by K positions.",
        "difficulty": "Medium",
        "category": "Arrays",
        "input_format": "N, array elements, and K.",
        "output_format": "Print rotated array.",
        "sample_input": "5\n1 2 3 4 5\n2",
        "sample_output": "4 5 1 2 3",
        "constraints": "1 <= N <= 100000"
    },
    {
        "title": "Palindrome Checker",
        "description": "Check whether a string reads the same forward and backward. Ignore case.",
        "difficulty": "Easy",
        "category": "Strings",
        "input_format": "A single string.",
        "output_format": "Print Yes or No.",
        "sample_input": "Madam",
        "sample_output": "Yes",
        "constraints": "1 <= string length <= 100000"
    },
    {
        "title": "First Non-Repeating Character",
        "description": "Find the first character that appears only once in a string. Print -1 if none exists.",
        "difficulty": "Medium",
        "category": "Strings",
        "input_format": "A single string.",
        "output_format": "Print the first non-repeating character or -1.",
        "sample_input": "swiss",
        "sample_output": "w",
        "constraints": "1 <= string length <= 100000"
    },
    {
        "title": "Binary Search",
        "description": "Find the index of a target in a sorted array using binary search.",
        "difficulty": "Easy",
        "category": "Searching",
        "input_format": "N, sorted array, and target.",
        "output_format": "Print index or -1.",
        "sample_input": "5\n1 3 5 7 9\n7",
        "sample_output": "3",
        "constraints": "1 <= N <= 1000000"
    },
    {
        "title": "Search in Rotated Sorted Array",
        "description": "Find a target in a rotated sorted array in O(log N) time.",
        "difficulty": "Medium",
        "category": "Searching",
        "input_format": "N, rotated array, and target.",
        "output_format": "Print index or -1.",
        "sample_input": "7\n4 5 6 7 0 1 2\n0",
        "sample_output": "4",
        "constraints": "1 <= N <= 100000"
    },
    {
        "title": "Sort an Array",
        "description": "Sort an array of integers in ascending order.",
        "difficulty": "Easy",
        "category": "Sorting",
        "input_format": "N followed by N integers.",
        "output_format": "Print sorted array.",
        "sample_input": "5\n5 2 8 1 3",
        "sample_output": "1 2 3 5 8",
        "constraints": "1 <= N <= 100000"
    },
    {
        "title": "Merge Two Sorted Arrays",
        "description": "Merge two sorted arrays into one sorted array.",
        "difficulty": "Medium",
        "category": "Sorting",
        "input_format": "N and M followed by both arrays.",
        "output_format": "Print merged sorted array.",
        "sample_input": "3 3\n1 3 5\n2 4 6",
        "sample_output": "1 2 3 4 5 6",
        "constraints": "1 <= N, M <= 100000"
    },
    {
        "title": "Valid Parentheses",
        "description": "Check whether brackets are correctly matched and nested.",
        "difficulty": "Easy",
        "category": "Data Structures",
        "input_format": "A string containing brackets.",
        "output_format": "Print True or False.",
        "sample_input": "()[]{}",
        "sample_output": "True",
        "constraints": "1 <= string length <= 10000"
    },
    {
        "title": "Queue Using Two Stacks",
        "description": "Implement a queue using two stacks with ENQUEUE, DEQUEUE, and FRONT operations.",
        "difficulty": "Medium",
        "category": "Data Structures",
        "input_format": "Q followed by Q queue operations.",
        "output_format": "Print results of FRONT operations.",
        "sample_input": "5\nENQUEUE 10\nENQUEUE 20\nFRONT\nDEQUEUE\nFRONT",
        "sample_output": "10\n20",
        "constraints": "1 <= Q <= 100000"
    },
    {
        "title": "Count Word Frequencies",
        "description": "Count the frequency of each word in a sentence and print words alphabetically.",
        "difficulty": "Easy",
        "category": "Python",
        "input_format": "A sentence.",
        "output_format": "Print each word and its frequency.",
        "sample_input": "apple banana apple orange banana apple",
        "sample_output": "apple 3\nbanana 2\norange 1",
        "constraints": "1 <= number of words <= 10000"
    },
    {
        "title": "Find Duplicate Elements",
        "description": "Find duplicate values in an array and print them in ascending order.",
        "difficulty": "Medium",
        "category": "Python",
        "input_format": "N followed by N integers.",
        "output_format": "Print duplicate values or -1.",
        "sample_input": "8\n1 2 3 2 4 5 1 6",
        "sample_output": "1 2",
        "constraints": "1 <= N <= 100000"
    },
    {
        "title": "Second Highest Salary",
        "description": "Write an SQL query to find the second-highest distinct salary from the Employee table.",
        "difficulty": "Medium",
        "category": "SQL",
        "input_format": "Employee table with id and salary columns.",
        "output_format": "Return the second-highest distinct salary or NULL.",
        "sample_input": "10000\n20000\n30000",
        "sample_output": "20000",
        "constraints": "Handle duplicate salaries."
    },
    {
        "title": "Employees Earning More Than Managers",
        "description": "Find employees whose salary is greater than their manager's salary using a self JOIN.",
        "difficulty": "Medium",
        "category": "SQL",
        "input_format": "Employee table with id, name, salary, and managerId.",
        "output_format": "Return qualifying employee names.",
        "sample_input": "Joe:70000:manager=3\nSam:60000",
        "sample_output": "Joe",
        "constraints": "Use a self JOIN."
    }

]