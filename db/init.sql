CREATE TABLE IF NOT EXISTS sessions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE NOT NULL,
  start_time TIME NULL,
  mode ENUM('boxing','strength','hybrid') NOT NULL DEFAULT 'boxing',
  intensity ENUM('low','medium','high') NOT NULL DEFAULT 'medium',
  duration_min INT NULL,
  notes TEXT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS session_exercises (
  id INT AUTO_INCREMENT PRIMARY KEY,
  session_id INT NOT NULL,
  type ENUM('boxing_rounds','strength','timed') NOT NULL,
  name VARCHAR(255) NOT NULL,

  rounds INT NULL,
  round_sec INT NULL,
  rest_sec INT NULL,
  focus VARCHAR(64) NULL,

  sets INT NULL,
  reps INT NULL,
  weight_value DECIMAL(10,2) NULL,
  weight_unit ENUM('kg','lb') NULL,
  weight_kg DECIMAL(10,4) NULL,

  duration_sec INT NULL,

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Optionnel : une table "exercises" si tu veux un catalogue
CREATE TABLE IF NOT EXISTS exercises (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  category VARCHAR(64) NOT NULL
);

INSERT INTO exercises (name, category)
SELECT * FROM (SELECT 'Corde à sauter', 'cardio') AS tmp
WHERE NOT EXISTS (SELECT 1 FROM exercises WHERE name='Corde à sauter')
LIMIT 1;

INSERT INTO exercises (name, category)
SELECT * FROM (SELECT 'Sac de frappe', 'technique') AS tmp
WHERE NOT EXISTS (SELECT 1 FROM exercises WHERE name='Sac de frappe')
LIMIT 1;

INSERT INTO exercises (name, category)
SELECT * FROM (SELECT 'Shadow boxing', 'technique') AS tmp
WHERE NOT EXISTS (SELECT 1 FROM exercises WHERE name='Shadow boxing')
LIMIT 1;
