-- database/schema.sql
CREATE DATABASE IF NOT EXISTS bluecollar_resume;
USE bluecollar_resume;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mobile VARCHAR(15) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    address TEXT,
    email VARCHAR(100),
    gender ENUM('Male', 'Female', 'Other', 'Prefer not to say'),
    profession VARCHAR(50),
    id_type VARCHAR(50),
    id_number VARCHAR(100),
    id_verified BOOLEAN DEFAULT FALSE,
    id_file_path VARCHAR(255),
    verification_data JSON,
    has_passkey BOOLEAN DEFAULT FALSE,
    passkey_data TEXT,
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_mobile (mobile),
    INDEX idx_profession (profession)
);

CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    template VARCHAR(50),
    file_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
);

CREATE TABLE IF NOT EXISTS job_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    job_title VARCHAR(100),
    company VARCHAR(100),
    location VARCHAR(100),
    description TEXT,
    salary_range VARCHAR(100),
    match_score INT,
    source VARCHAR(50),
    apply_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
);

CREATE TABLE IF NOT EXISTS user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    session_token VARCHAR(255) UNIQUE,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (session_token),
    INDEX idx_user_id (user_id)
);

CREATE TABLE IF NOT EXISTS professions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    icon_class VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample professions
INSERT IGNORE INTO professions (name, icon_class, description) VALUES
('Electrician', 'fas fa-bolt', 'Electrical installation and repair specialist'),
('Plumber', 'fas fa-faucet', 'Pipe fitting and water systems expert'),
('Carpenter', 'fas fa-hammer', 'Woodworking and construction professional'),
('Driver', 'fas fa-truck', 'Commercial and personal vehicle operator'),
('Welder', 'fas fa-fire', 'Metal joining and fabrication specialist'),
('Mechanic', 'fas fa-tools', 'Vehicle repair and maintenance expert'),
('Construction Worker', 'fas fa-hard-hat', 'General construction laborer'),
('Painter', 'fas fa-paint-roller', 'Surface coating and finishing professional'),
('Mason', 'fas fa-border-style', 'Brick and stone work specialist'),
('Gardener', 'fas fa-leaf', 'Landscaping and plant care expert'),
('Security Guard', 'fas fa-shield-alt', 'Safety and security personnel'),
('Cleaner', 'fas fa-broom', 'Sanitation and cleaning professional');