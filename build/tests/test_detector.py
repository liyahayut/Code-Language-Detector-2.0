import pytest

from detector import LanguageDetector

detector = LanguageDetector()

SAMPLES = {
    "Python": """
import os

class Greeter:
    def __init__(self, name):
        self.name = name

    def greet(self):
        if self.name:
            print(f"Hello, {self.name}!")
        elif not self.name:
            print("Hello, stranger!")
""",
    "JavaScript": """
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    console.log("request received");
    res.send('Hello World');
});

document.querySelector('#app').innerHTML = 'ready';
""",
    "TypeScript": """
interface User {
    id: number;
    name: string;
}

class UserService implements Repository<User> {
    getUser(id: number): User | undefined {
        return this.users.find(u => u.id === id);
    }
}
""",
    "Java": """
import java.util.List;

public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, world!");
        List<String> names = new ArrayList<>();
    }
}
""",
    "C++": """
#include <iostream>
using namespace std;

int main() {
    std::vector<int> nums;
    cout << "Hello, world!" << endl;
    return 0;
}
""",
    "C": """
#include <stdio.h>

typedef struct Point {
    int x;
    int y;
} Point;

int main(void) {
    Point *p = malloc(sizeof(Point));
    printf("Hello, world!\\n");
    return 0;
}
""",
    "C#": """
using System;

namespace HelloApp {
    public class Program {
        public static void Main(string[] args) {
            Console.WriteLine("Hello, world!");
        }
    }
}
""",
    "Go": """
package main

import (
    "fmt"
)

func main() {
    message := "Hello, world!"
    fmt.Println(message)
}
""",
    "Ruby": """
require 'json'

class Greeter
  def initialize(name)
    @name = name
  end

  def greet
    puts "Hello, #{@name}!"
  end
end

[1, 2, 3].each do |n|
  puts n
end
""",
    "PHP": """
<?php
function greet($name) {
    echo "Hello, " . $name;
}

$user = "world";
greet($user);
""",
    "Rust": """
use std::collections::HashMap;

fn main() {
    let mut scores = HashMap::new();
    scores.insert("Blue", 10);
    println!("{:?}", scores);
}

impl Greeter {
    fn greet(&self) -> String {
        format!("hello")
    }
}
""",
    "HTML": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Home</title>
</head>
<body>
    <div id="app"></div>
</body>
</html>
""",
    "CSS": """
.container {
    display: flex;
    padding: 1rem;
}

#header:hover {
    color: red;
}

@media (max-width: 600px) {
    .container { flex-direction: column; }
}
""",
    "SQL": """
SELECT users.id, users.name
FROM users
JOIN orders ON orders.user_id = users.id
WHERE orders.total > 100;

INSERT INTO logs (message) VALUES ('done');
""",
    "Bash": """
#!/bin/bash
if [ -z "$1" ]; then
    echo "usage: $0 <name>"
    exit 1
fi
echo "Hello, $1!"
""",
    "JSON": """
{
  "name": "code-language-detector",
  "version": "2.0.0",
  "private": true
}
""",
}


@pytest.mark.parametrize("expected_language", SAMPLES.keys())
def test_detects_expected_language(expected_language):
    code = SAMPLES[expected_language]
    result = detector.detect(code)
    assert result.language == expected_language, (
        f"expected {expected_language}, got {result.language} "
        f"(scores: {result.scores})"
    )
    assert result.confidence > 0


def test_empty_input_returns_none():
    result = detector.detect("")
    assert result.language is None
    assert result.confidence == 0.0


def test_whitespace_only_input_returns_none():
    result = detector.detect("   \n\t  ")
    assert result.language is None


def test_extension_hint_breaks_ties():
    # deliberately ambiguous snippet that could plausibly be several languages
    ambiguous = "x = 1"
    result = detector.detect(ambiguous, filename="script.py")
    assert result.language == "Python"


def test_ranked_returns_sorted_scores():
    result = detector.detect(SAMPLES["Python"])
    ranked = result.ranked()
    scores = [score for _, score in ranked]
    assert scores == sorted(scores, reverse=True)


def test_matched_rules_are_explainable():
    result = detector.detect(SAMPLES["SQL"])
    assert result.language == "SQL"
    assert len(result.matched_rules["SQL"]) > 0
