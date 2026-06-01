CREATE TABLE agencies  (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL 
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    agency_id INT REFERENCES agencies(id),
    is_active BOOLEAN NOT NULL,
    created_at TIMESTAMP
);

CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    address VARCHAR(255) NOT NULL, 
    size_sqm FLOAT NOT NULL, 
    monthly_price DECIMAL NOT NULL,
    agency_id INT NOT NULL REFERENCES agencies(id), 
    is_occupied BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    start_date DATE NOT NULL, 
    end_date DATE NOT NULL,
    property_id INT NOT NULL REFERENCES properties(id),
    user_id INT NOT NULL REFERENCES users(id),
    created_at TIMESTAMP
);
