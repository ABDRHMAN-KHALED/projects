CREATE TABLE learner(
    id INT PRIMARY KEY,
    name VARCHAR(37),
    number INT UNIQUE,
    gmail VARCHAR(30),
    password VARCHAR(33),
    repass VARCHAR(33),
    balance FLOAT,
    register_time TIMESTAMP
);

CREATE TABLE trainer(
    id INT PRIMARY KEY,
    name VARCHAR(37),
    number INT UNIQUE,
    gmail VARCHAR(30),
    password VARCHAR(33),
    repass VARCHAR(33),
    balance FLOAT,
    register_time TIMESTAMP,
    commercial_registration_on VARCHAR(44),
    work VARCHAR(35),
    ip VARCHAR(13),
    image VARCHAR(44),
    background VARCHAR(38),
    your_linkedin VARCHAR(75)
);

CREATE TABLE course(
    id INT PRIMARY KEY,
    name VARCHAR(33) NOT NULL,
    summary_script VARCHAR(36),
    video_course VARCHAR(38),
    type VARCHAR(29),
    trainer_id INT NOT NULL,
    FOREIGN KEY (trainer_id) REFERENCES trainer(id)
);

CREATE TABLE test(
    id INT PRIMARY KEY,
    name VARCHAR(34),
    place VARCHAR(29),
    period TIME,
    questions_form VARCHAR(50),
    answer_form VARCHAR(50),
    data DATE,
    location VARCHAR(37),
    trainer_id INT NOT NULL,
    course_id INT NOT NULL,
    FOREIGN KEY (trainer_id) REFERENCES trainer(id),
    FOREIGN KEY (course_id) REFERENCES course(id)
);

CREATE TABLE financial_tr(
    id TINYINT PRIMARY KEY,
    payment_user VARCHAR(35),
    amount FLOAT,
    status VARCHAR(33),
    type VARCHAR(29),
    trainer_id INT,
    FOREIGN KEY (trainer_id) REFERENCES trainer(id)
);

CREATE TABLE financial_le(
    id TINYINT PRIMARY KEY,
    payment_user VARCHAR(35),
    amount FLOAT,
    status VARCHAR(33),
    type VARCHAR(29),
    trainer_id INT,
    screen VARCHAR(33),
    payment_options FLOAT,
    FOREIGN KEY (trainer_id) REFERENCES trainer(id)
);

CREATE TABLE answer_test(
    id SMALLINT PRIMARY KEY,
    document VARCHAR(34),
    learner_id INT NOT NULL,
    trainer_id INT NOT NULL,
    test_id INT NOT NULL,
    FOREIGN KEY (learner_id) REFERENCES learner(id),
    FOREIGN KEY (trainer_id) REFERENCES trainer(id),
    FOREIGN KEY (test_id) REFERENCES test(id)
);

CREATE TABLE learner_support(
    id INT PRIMARY KEY,
    best_communication VARCHAR(44),
    message VARCHAR(33),
    time TIMESTAMP,
    any_document VARCHAR(38),
    contact_address VARCHAR(40),
    learner_id INT NOT NULL,
    FOREIGN KEY (learner_id) REFERENCES learner(id)
);

CREATE TABLE reply_problem_le(
    id SMALLINT PRIMARY KEY,
    learner_id INT NOT NULL,
    time TIMESTAMP,
    any_document VARCHAR(39),
    reply VARCHAR(33),
    FOREIGN KEY (learner_id) REFERENCES learner(id)
);

CREATE TABLE trainer_support(
    id INT PRIMARY KEY,
    best_communication VARCHAR(44),
    message VARCHAR(33),
    time TIMESTAMP,
    any_document VARCHAR(38),
    contact_address VARCHAR(40),
    trainer_id INT NOT NULL,
    FOREIGN KEY (trainer_id) REFERENCES trainer(id)
);

CREATE TABLE courses_revenue(
    id INT PRIMARY KEY,
    amount VARCHAR(39),
    data DATE,
    trainer_id INT NOT NULL,
    FOREIGN KEY (trainer_id) REFERENCES trainer(id)
);

CREATE TABLE buy_transactions(
    id INT PRIMARY KEY,
    trainer_id INT NOT NULL,
    course_id INT NOT NULL,
    learner_id INT NOT NULL,
    count_star INT,
    FOREIGN KEY (trainer_id) REFERENCES trainer(id),
    FOREIGN KEY (course_id) REFERENCES course(id) ,
    FOREIGN KEY (learner_id) REFERENCES learner(id)
);

CREATE TABLE react_course(
    id INT PRIMARY KEY,
    trainer_id INT NOT NULL,
    course_id INT NOT NULL,
    learner_id INT NOT NULL,
    count_star INT,
    FOREIGN KEY (trainer_id) REFERENCES trainer(id),
    FOREIGN KEY (course_id) REFERENCES course(id) ,
    FOREIGN KEY (learner_id) REFERENCES learner(id)
);

CREATE TABLE test_valuation(
    id INT PRIMARY KEY,
    trainer_id INT NOT NULL,
    learner_id INT NOT NULL,
    test_name VARCHAR(44),
    learner_name VARCHAR(44),
    percentage FLOAT,
    certificate VARCHAR(29),
    status VARCHAR(50),
    test_id INT NOT NULL,
    FOREIGN KEY (trainer_id) REFERENCES trainer(id),
    FOREIGN KEY (learner_id) REFERENCES learner(id),
    FOREIGN KEY (test_id) REFERENCES test(id)
);

CREATE TABLE reply_problem_tr(
    id INT PRIMARY KEY,
    trainer_id INT NOT NULL,
    reply VARCHAR(44),
    time TIMESTAMP,
    any_document VARCHAR(33),
    FOREIGN KEY (trainer_id) REFERENCES trainer(id)
);
