-- DROP DATABASE IF EXISTS college_canteen;

create database college_canteen;
use college_canteen;

CREATE TABLE Food (
    F_item_no INT PRIMARY KEY,
    F_name VARCHAR(50),
    F_type VARCHAR(30),
    F_price DECIMAL(10,2)
);

CREATE TABLE Customer (
    customer_id INT PRIMARY KEY ,
    c_name VARCHAR(50),
    ph_no VARCHAR(15),
    address VARCHAR(100),
    first_name VARCHAR(30),
    middle_name VARCHAR(30),
    last_name VARCHAR(30)
);

CREATE TABLE Administrator (
    admin_id INT PRIMARY KEY,
    A_name VARCHAR(50),
    address VARCHAR(100)
);

CREATE TABLE Phone_numbers (
    admin_id INT,
    ph_no VARCHAR(10),
    PRIMARY KEY (admin_id, ph_no),
    FOREIGN KEY (admin_id) REFERENCES Administrator(admin_id)
);

CREATE TABLE Orders (
    order_id INT PRIMARY KEY,
    order_date DATE,
    order_No VARCHAR(20),
    user_id INT,
    quantity INT,
    customer_id INT,
    admin_id INT,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (admin_id) REFERENCES Administrator(admin_id)
);

CREATE TABLE Item (
    item_id INT PRIMARY KEY,
    I_name VARCHAR(50),
    description VARCHAR(100),
    price DECIMAL(10,2),
    order_id INT,
    customer_id INT,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

CREATE TABLE Staff (
    staff_id INT PRIMARY KEY,
    staff_name VARCHAR(50),
    order_id INT,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);

CREATE TABLE Offer (
	offer_id INT,
    offer_amt DECIMAL(10,2),
    start_date DATE,
    end_date DATE,
    item_id INT,
	PRIMARY KEY(item_id,offer_id),
    staff_id INT,
    FOREIGN KEY (item_id) REFERENCES Item(item_id),
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id)
);

CREATE TABLE Bill (
    bill_id INT PRIMARY KEY,
    bill_amount DECIMAL(10,2),
    bill_date DATE,
    customer_id INT,
    order_id INT,
    admin_id INT,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (admin_id) REFERENCES Administrator(admin_id)
);
CREATE TABLE Delivered (
    customer_id INT,
    F_item_no INT,
    PRIMARY KEY(customer_id,F_item_no),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (F_item_no) REFERENCES Food(F_item_no)
);

CREATE TABLE Selects (
    customer_id INT,
    item_id INT,
    PRIMARY KEY(customer_id,item_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (item_id) REFERENCES Item(item_id)
);
INSERT INTO Food (F_item_no, F_name, F_type, F_price) VALUES
(1, 'Margherita Pizza', 'Veg', 299.00),
(2, 'Chicken Burger', 'Non-Veg', 199.50),
(3, 'Pasta Alfredo', 'Veg', 249.75);


INSERT INTO Customer (customer_id, c_name, ph_no, address, first_name, middle_name, last_name) VALUES
(1, 'Alice Smith', '9876543210', '123 Main St, City', 'Alice', 'M', 'Smith'),
(2, 'Bob Johnson', '9123456780', '456 Lake View, Town', 'Bob', 'A', 'Johnson'),
(3, 'Carol White', '9988776655', '789 Green Park, City', 'Carol', NULL, 'White');
desc customer;
select *from customer;

INSERT INTO Administrator (admin_id, A_name, address) VALUES
(1, 'Admin One', 'HQ Building, City'),
(2, 'Admin Two', 'Branch Office, Town'),
(3, 'Admin Three', 'Warehouse Street, City');

INSERT INTO Phone_numbers (admin_id, ph_no) VALUES
(1, '9000000001'),
(2, '9000000002'),
(3, '9000000003');

INSERT INTO Orders (order_id, order_date, order_No, user_id, quantity, customer_id, admin_id) VALUES
(1, '2025-10-01', 'ORD001', 101, 2, 1, 1),
(2, '2025-10-02', 'ORD002', 102, 1, 2, 2),
(3, '2025-10-03', 'ORD003', 103, 3, 3, 3);

INSERT INTO Item (item_id, I_name, description, price, order_id, customer_id) VALUES
(1, 'Pizza', 'Cheesy Margherita', 299.00, 1, 1),
(2, 'Burger', 'Grilled Chicken', 199.50, 2, 2),
(3, 'Pasta', 'Creamy Alfredo', 249.75, 3, 3);

INSERT INTO Staff (staff_id, staff_name, order_id) VALUES
(1, 'John', 1),
(2, 'Mary', 2),
(3, 'Steve', 3);

INSERT INTO Offer (offer_id, offer_amt, start_date, end_date, item_id, staff_id) VALUES
(1, 50.00, '2025-10-01', '2025-10-10', 1, 1),
(2, 30.00, '2025-10-05', '2025-10-15', 2, 2),
(3, 20.00, '2025-10-08', '2025-10-18', 3, 3);

INSERT INTO Bill (bill_id, bill_amount, bill_date, customer_id, order_id, admin_id) VALUES
(1, 548.00, '2025-10-01', 1, 1, 1),
(2, 199.50, '2025-10-02', 2, 2, 2),
(3, 699.25, '2025-10-03', 3, 3, 3);

INSERT INTO Delivered (customer_id, F_item_no) VALUES
(1, 1),
(2, 2),
(3, 3);

INSERT INTO Selects (customer_id, item_id) VALUES
(1, 1),
(2, 2),
(3, 3);
-- select * from selects;
SHOW TABLES;

-- ==========================================================
-- TRIGGERS
-- ==========================================================
-- Trigger 1: Prevent Negative Bill Amounts
DELIMITER //
CREATE TRIGGER check_bill_amount
BEFORE INSERT ON Bill
FOR EACH ROW
BEGIN
    IF NEW.bill_amount <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Bill amount must be greater than zero';
    END IF;
END //
DELIMITER ;

-- Trigger 2: Automatically Generate Bill when New Order is Inserted
DELIMITER //
CREATE TRIGGER after_order_insert
AFTER INSERT ON Orders
FOR EACH ROW
BEGIN
    INSERT INTO Bill (bill_id, bill_amount, bill_date, customer_id, order_id, admin_id)
    VALUES (
        NEW.order_id,
        NEW.quantity * 100,  -- Example calculation (100 per item)
        CURDATE(),
        NEW.customer_id,
        NEW.order_id,
        NEW.admin_id
    );
END //
DELIMITER ;

-- ==========================================================
-- PROCEDURES
-- ==========================================================
-- Procedure 1: List All Orders by a Given Customer
DELIMITER //
CREATE PROCEDURE get_customer_orders(IN custId INT)
BEGIN
    SELECT order_id, order_date, quantity
    FROM Orders
    WHERE customer_id = custId;
END //
DELIMITER ;

-- Procedure 2: Compute Total Bill Amount for a Customer
DELIMITER //
CREATE PROCEDURE GetTotalBill(IN cust_id INT)
BEGIN
    SELECT SUM(bill_amount) AS Total_Bill
    FROM Bill
    WHERE customer_id = cust_id;
END //
DELIMITER ;

-- ==========================================================
-- FUNCTIONS
-- ==========================================================

-- Function 2: Apply Discount on a Price
DELIMITER //
CREATE FUNCTION ApplyDiscount(price DECIMAL(10,2), discount DECIMAL(10,2))
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    RETURN price - (price * discount / 100);
END //
DELIMITER ;

-- Trigger 1: Prevent Negative Bill Amounts
USE college_canteen;
INSERT INTO Bill (bill_id, bill_amount, bill_date, customer_id, order_id, admin_id)
VALUES (10, 0, '2025-10-10', 1, 1, 1);
SELECT * FROM Bill WHERE bill_id = 10;

-- Trigger 2: Automatically Generate Bill when New Order is Inserted
-- Insert a new order
INSERT INTO Orders (order_id, order_date, order_No, user_id, quantity, customer_id, admin_id)
VALUES (5, '2025-10-30', 'ORD005', 104, 3, 2, 2);
SELECT * FROM Bill WHERE bill_id = 5;

-- Procedure 1: List All Orders by a Given Customer
CALL get_customer_orders(2);
-- CALL get_customer_orders(2);


-- Procedure 2: Compute Total Bill Amount for a Customer
CALL GetTotalBill(1);
CALL GetTotalBill(2);



-- Function 2: Apply Discount on a Price
SELECT ApplyDiscount(500, 10) AS DiscountedPrice;
SELECT APPLYDISCOUNT(200, 25) AS DiscountedPrice;

SHOW CREATE PROCEDURE GetTotalBill;
SHOW CREATE PROCEDURE get_customer_orders;
show triggers;

SHOW FUNCTION STATUS WHERE Db = 'college_canteen';
