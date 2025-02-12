CREATE DATABASE order_supply_schema;
USE order_supply_schema;

-- Suppliers Table
CREATE TABLE Suppliers (
    Id INT PRIMARY KEY,
    CompanyName VARCHAR(255),
    ContactName VARCHAR(255),
    ContactTitle VARCHAR(255),
    City VARCHAR(255),
    Country VARCHAR(255),
    Phone VARCHAR(50),
    Fax VARCHAR(50)
);

-- Products Table
CREATE TABLE Products (
    Id INT PRIMARY KEY,
    ProductName VARCHAR(255),
    SupplierId INT,
    UnitPrice DECIMAL(10, 2),
    Package VARCHAR(255),
    IsDiscontinued BIT,
    FOREIGN KEY (SupplierId) REFERENCES Suppliers(Id)
);

-- Customers Table
CREATE TABLE Customers (
    Id INT PRIMARY KEY,
    FirstName VARCHAR(255),
    LastName VARCHAR(255),
    City VARCHAR(255),
    Country VARCHAR(255),
    Phone VARCHAR(50)
);

-- Orders Table
CREATE TABLE Orders (
    Id INT PRIMARY KEY,
    OrderDate DATETIME,
    OrderNumber VARCHAR(255),
    CustomerId INT,
    TotalAmount DECIMAL(10, 2),
    FOREIGN KEY (CustomerId) REFERENCES Customers(Id)
);

-- OrderItem Table
CREATE TABLE OrderItem (
    Id INT PRIMARY KEY,
    OrderId INT,
    ProductId INT,
    Quantity DECIMAL(10, 2),
    UnitPrice DECIMAL(10, 2),
    FOREIGN KEY (OrderId) REFERENCES Orders(Id),
    FOREIGN KEY (ProductId) REFERENCES Products(Id)
);
CREATE DATABASE order_supply_schema;
USE order_supply_schema;

CREATE TABLE Suppliers (
    Id INT PRIMARY KEY,
    CompanyName VARCHAR(255),
    ContactName VARCHAR(255),
    ContactTitle VARCHAR(255),
    City VARCHAR(100),
    Country VARCHAR(100),
    Phone VARCHAR(50),
    Fax VARCHAR(50)
);

CREATE TABLE Products (
    Id INT PRIMARY KEY,
    ProductName VARCHAR(255),
    SupplierId INT,
    UnitPrice DECIMAL(10, 2),
    Package VARCHAR(100),
    IsDiscontinued BIT,
    FOREIGN KEY (SupplierId) REFERENCES Suppliers(Id)
);

CREATE TABLE Customers (
    Id INT PRIMARY KEY,
    FirstName VARCHAR(255),
    LastName VARCHAR(255),
    City VARCHAR(100),
    Country VARCHAR(100),
    Phone VARCHAR(50)
);

CREATE TABLE Orders (
    Id INT PRIMARY KEY,
    OrderDate DATETIME,
    OrderNumber VARCHAR(100),
    CustomerId INT,
    TotalAmount DECIMAL(10, 2),
    FOREIGN KEY (CustomerId) REFERENCES Customers(Id)
);

CREATE TABLE OrderItem (
    Id INT PRIMARY KEY,
    OrderId INT,
    ProductId INT,
    Quantity DECIMAL(10, 2),
    UnitPrice DECIMAL(10, 2),
    FOREIGN KEY (OrderId) REFERENCES Orders(Id),
    FOREIGN KEY (ProductId) REFERENCES Products(Id)
);

INSERT INTO Suppliers (Id, CompanyName, ContactName, ContactTitle, City, Country, Phone, Fax)
VALUES
(1, 'Supplier A', 'Alice', 'Manager', 'Paris', 'France', '123456789', '987654321'),
(2, 'Supplier B', 'Bob', 'Director', 'Berlin', 'Germany', '223344556', '654321987'),
(3, 'Supplier C', 'Charlie', 'Sales', 'London', 'UK', '334455667', '321987654');

INSERT INTO Products (Id, ProductName, SupplierId, UnitPrice, Package, IsDiscontinued)
VALUES
(1, 'Product X', 1, 150.00, 'Box', 0),
(2, 'Product Y', 2, 75.50, 'Bag', 1),
(3, 'Product Z', 3, 200.00, 'Bottle', 0);

INSERT INTO Customers (Id, FirstName, LastName, City, Country, Phone)
VALUES
(1, 'John', 'Doe', 'New York', 'USA', '5551234567'),
(2, 'Jane', 'Smith', 'Los Angeles', 'USA', '5559876543'),
(3, 'Emily', 'Davis', 'Toronto', 'Canada', '5555678901');

INSERT INTO Orders (Id, OrderDate, OrderNumber, CustomerId, TotalAmount)
VALUES
(1, '2023-01-15', 'ORD001', 1, 300.00),
(2, '2023-02-20', 'ORD002', 2, 450.00),
(3, '2024-01-10', 'ORD003', 1, 150.00);

INSERT INTO OrderItem (Id, OrderId, ProductId, Quantity, UnitPrice)
VALUES
(1, 1, 1, 2, 150.00),
(2, 2, 2, 5, 75.50),
(3, 3, 3, 1, 200.00);

SELECT CompanyName 
FROM Suppliers 
WHERE Country = 'France';

SELECT COUNT(*) AS JanuaryOrders 
FROM Orders 
WHERE MONTH(OrderDate) = 1;

SELECT Customers.FirstName, Customers.LastName 
FROM Customers
JOIN Orders ON Customers.Id = Orders.CustomerId
GROUP BY Customers.Id
HAVING COUNT(Orders.Id) >= 3;

SELECT ProductName, UnitPrice 
FROM Products 
WHERE UnitPrice > 100;

SELECT Products.ProductName, SUM(OrderItem.Quantity) AS TotalQuantity 
FROM OrderItem
JOIN Products ON OrderItem.ProductId = Products.Id
GROUP BY Products.Id
ORDER BY TotalQuantity DESC
LIMIT 1;

SELECT ProductName, UnitPrice 
FROM Products 
ORDER BY UnitPrice DESC
LIMIT 3;

SELECT FirstName, LastName 
FROM Customers 
WHERE Id NOT IN (
    SELECT CustomerId 
    FROM Orders 
    WHERE YEAR(OrderDate) = 2014
);

SELECT Products.ProductName, Products.UnitPrice, Suppliers.CompanyName 
FROM Products
JOIN Suppliers ON Products.SupplierId = Suppliers.Id
WHERE Products.IsDiscontinued = 1;

SELECT Suppliers.CompanyName 
FROM Suppliers
JOIN Products ON Suppliers.Id = Products.SupplierId
GROUP BY Suppliers.Id
HAVING COUNT(Products.Id) > 5;

SELECT Customers.City, SUM(Orders.TotalAmount) AS TotalRevenue 
FROM Customers
JOIN Orders ON Customers.Id = Orders.CustomerId
WHERE Customers.Country = 'USA'
GROUP BY Customers.City;

SELECT Products.ProductName 
FROM Products
JOIN OrderItem ON Products.Id = OrderItem.ProductId
JOIN Orders ON OrderItem.OrderId = Orders.Id
JOIN Customers ON Orders.CustomerId = Customers.Id
GROUP BY Products.Id
HAVING COUNT(DISTINCT Customers.City) > 3;

SELECT Suppliers.CompanyName, AVG(Orders.TotalAmount) AS AverageOrderValue 
FROM Suppliers
JOIN Products ON Suppliers.Id = Products.SupplierId
JOIN OrderItem ON Products.Id = OrderItem.ProductId
JOIN Orders ON OrderItem.OrderId = Orders.Id
GROUP BY Suppliers.Id;

SELECT Products.ProductName 
FROM Products
GROUP BY Products.ProductName
HAVING COUNT(DISTINCT Products.SupplierId) > 1;

SELECT DISTINCT Suppliers.CompanyName 
FROM Suppliers
JOIN Products ON Suppliers.Id = Products.SupplierId
WHERE Products.UnitPrice > (SELECT AVG(UnitPrice) FROM Products);

SELECT Customers.FirstName, Customers.LastName 
FROM Customers
JOIN Orders ON Customers.Id = Orders.CustomerId
JOIN OrderItem ON Orders.Id = OrderItem.OrderId
JOIN Products ON OrderItem.ProductId = Products.Id
JOIN Suppliers ON Products.SupplierId = Suppliers.Id
GROUP BY Customers.Id
HAVING COUNT(DISTINCT Suppliers.Country) > 2;
