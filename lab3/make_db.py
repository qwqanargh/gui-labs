
import sqlite3
from pathlib import Path

path = Path(__file__).resolve().parent / "university.db"
path.unlink(missing_ok=True)
con = sqlite3.connect(path)
con.executescript("""
CREATE TABLE groups (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL,
    course  INTEGER NOT NULL
);
CREATE TABLE students (
    id        INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    group_id  INTEGER REFERENCES groups(id),
    birth     TEXT
);
CREATE TABLE subjects (
    id     INTEGER PRIMARY KEY,
    title  TEXT NOT NULL,
    hours  INTEGER
);
CREATE TABLE grades (
    student_id INTEGER REFERENCES students(id),
    subject_id INTEGER REFERENCES subjects(id),
    mark       INTEGER CHECK (mark BETWEEN 2 AND 5)
);
CREATE INDEX idx_students_group ON students(group_id);
CREATE VIEW avg_marks AS
    SELECT s.full_name, ROUND(AVG(g.mark), 2) AS avg_mark
    FROM students s JOIN grades g ON g.student_id = s.id
    GROUP BY s.id;
""")
con.executemany("INSERT INTO groups VALUES (?,?,?)",
                [(1, "6231", 3), (2, "6232", 3), (3, "6233", 3)])
con.executemany("INSERT INTO students VALUES (?,?,?,?)", [
    (1, "Алексеев Пётр", 1, "2005-03-14"), (2, "Белова Анна", 1, "2005-07-02"),
    (3, "Васильев Олег", 2, "2004-11-23"), (4, "Григорьева Мария", 2, "2005-01-30"),
    (5, "Дмитриев Илья", 3, "2005-05-09"), (6, "Егорова Софья", 3, "2005-09-17"),
    (7, "Жуков Никита", 3, "2004-12-05"),
])
con.executemany("INSERT INTO subjects VALUES (?,?,?)", [
    (1, "Графический интерфейс", 72), (2, "Базы данных", 108),
    (3, "Математический анализ", 144), (4, "Английский язык", 72),
])
marks = [5, 4, 5, 3, 4, 4, 5, 5, 3, 4, 4, 5, 5, 5, 4, 3, 4, 5, 3, 4, 5, 4, 5, 4, 4, 3, 5, 5]
con.executemany("INSERT INTO grades VALUES (?,?,?)",
                [(s, subj, marks[(s - 1) * 4 + subj - 1]) for s in range(1, 8) for subj in range(1, 5)])
con.commit()
con.close()
print("Создана", path)
