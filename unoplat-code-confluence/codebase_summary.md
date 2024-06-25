```markdown

[Order]
=========

**Package**: `com.datastax.examples.order`

**File Path**: `src/main/java/com/datastax/examples/order/Order.java`

**Responsibility**: The `Order` class represents a customer's order, including the product details and timestamp when it was added to the system. It is designed for use with Cassandra database integration through Spring Data.

## Fields

- **OrderPrimaryKey (com.datastax.examples.order.OrderPrimaryKey)**: Represents a unique identifier for each order entry in the Cassandra table, ensuring data integrity and efficient querying. It is marked with `@PrimaryKey` annotation to signify its role as the primary key of the `Order` class.

- **Integer (productQuantity)**: Stores the quantity of products ordered by the customer. Annotated with `@Column("product_quantity")` and `@CassandraType(type = CassandraType.Name.INT)` to map it correctly within the Cassandra database schema.

- **String (productName)**: Holds the name of the product being ordered, which is essential for identifying the items in an order. Annotated with `@Column("product_name")` and `@CassandraType(type = CassandraType.Name.TEXT)` to map it correctly within the Cassandra database schema.

- **Float (productPrice)**: Contains the price of a single product unit, used for calculating the total order cost based on quantity. Annotated with `@CassandraType(type = CassandraType.Name.DECIMAL)` to map it correctly within the Cassandra database schema.

- **Instant (addedToOrderTimestamp)**: Records the timestamp when an order was added to the system, providing a reference for processing times and auditing purposes. Annotated with `@Column("added_to_order_at")` and `@CassandraType(type = CassandraType.Name.TIMESTAMP)` to map it correctly within the Cassandra database schema.
```

Class Summary: The `OrderController` class is responsible for managing HTTP requests related to order management, including creating, updating, deleting orders and fetching order details. It interacts with an `OrderRepository` to access data from a database or any other storage system.

Package: com.datastax.examples.order
File Path: src/main/java/com.datastax.examples/order/OrderController.java
Responsibility: Manages HTTP requests for order operations, including creating, updating, deleting orders and fetching order details by interacting with OrderRepository to access data from a database or other storage system.

## Fields
- **OrderRepository**: `private OrderRepository orderRepository`
  - Type: Repository class responsible for storing and retrieving data related to orders in the underlying storage system (e.g., relational databases, NoSQL databases). It provides methods such as save(), findByKeyOrderId(), etc.

## Methods
- **root()**: `ModelAndView` - Returns a view name and model attributes for rendering the main page of order management. This method is typically used to display the list of orders or an empty state in the UI.
- **createOrder(HttpServletRequest request, HttpServletResponse response)**: `Order` - Creates a new order based on user input from the HTTP request and persists it using OrderRepository's save() method. It also handles any exceptions that may occur during the process.
- **updateOrder(Long orderId, Order updatedOrder, Model model)**: `Order` - Updates an existing order with a given ID by setting its key properties (e.g., order id and product id), persisting it using OrderRepository's save() method, and updating the corresponding view in the UI.
- **deleteOrder(Long orderId, Model model)**: `void` - Deletes an existing order with a given ID by removing it from the storage system through OrderRepository's deleteByKeyOrderIdAndKeyProductId() or deleteByKeyOrderId() methods based on whether product id is provided.
- **findOrder(Long orderId, Model model)**: `ProductNameAndPrice` - Retrieves a single order detail (including its name and price information) for the given order ID using OrderRepository's findByKeyOrderIdAndKeyProductId() method. It also handles any exceptions that may occur during retrieval.
- **findOrders(Model model)**: `List<ProductNameAndPrice>` - Retrieves a list of all orders and their corresponding details (including name and price information) by invoking OrderRepository's findByKeyOrderId() method for each order ID present in the storage system.
- **findAll(Model model)**: `List<ProductNameAndPrice>` - Retrieves a paginated list of all orders and their corresponding details (including name and price information) by invoking OrderRepository's findAllProjectedBy() method with appropriate parameters for page size, current page number, etc.

In summary, the `OrderController` class serves as an intermediary between the user interface and the underlying storage system to manage order-related operations in a web application using Spring MVC framework conventions.

```markdown
[OrderPrimaryKey]

- **Package**: `com.datastax.examples.order`
- **File Path**: `src/main/java/com/datastax/examples/order/OrderPrimaryKey.java`
- **Responsibility**: This class represents the primary key for an order entity, composed of two UUID fields that uniquely identify each order and product combination in a Cassandra database schema.

## Fields

- **UUID orderId**
  - **Type**: `private UUID` – The partition key component identifying the unique order within its partition. It is annotated with `@PrimaryKeyColumn(name = "order_id", ordinal = 0, type = PrimaryKeyType.PARTITIONED)` to designate it as part of the primary key.

- **UUID productId**
  - **Type**: `private UUID` – The clustering column component identifying the unique product within an order. It is annotated with `@PrimaryKeyColumn(name = "product_id", ordinal = 1, type = PrimaryKeyType.CLUSTERED)` to designate it as part of the primary key.

## Methods
```

Validation: The markdown output correctly follows the specification provided by the user and is structured with appropriate headings for class summary, fields, and methods sections.

## Class Summary:
SwaggerConfig class is responsible for configuring and providing Swagger UI documentation for a REST API. It defines customizable metadata about the API, including contact details, license information, and group name. This class is specifically designed to generate Swagger 2.0 compliant API documentation for the orders section of an application powered by DataStax Cassandra.

## Fields:
The SwaggerConfig class does not have any fields (member variables).

## Methods:
- **api()**: `Docket`
  - **Summary**: This method configures and returns a Docket instance, which represents the API documentation for orders in Swagger UI. It sets up various properties such as group name, selects all available endpoints, filters by specific paths (/orders/**), builds the final configuration, and attaches API information to it.
  - **Internal Calls**:
    - `apiInfo()` method is called within this method to obtain the ApiInfo instance required for setting up Swagger UI metadata.
  - **External Calls**:
    - `Docket.`groupName("orders")` sets a group name ("orders") to categorize the API documentation in Swagger UI.
    - `newDocket.`select()` initializes a selection process on the endpoints provided by Spring MVC and WebFlux controllers, including handler mappings, message converters, argument resolvers, etc.
    - `RequestHandlerSelectors.`any()` specifies that any request should be included in this API documentation. This selector returns true for all handlers of interest.
    - `newDocket.`paths(PathSelectors.`ant("/orders/**"))` filters the endpoints to include only those with paths starting with "/orders/".
    - `newDocket.`build()` method constructs a new Docket instance that incorporates all properties defined within this method (e.g., group name, selection of request handlers, path filters).
    - `newDocket.`apiInfo(ApiInfo apiInfo)` attaches the ApiInfo object returned from the `apiInfo()` method to the final configuration. This object contains metadata like title, description, contact details, license information, and additional documentation links for Swagger UI display purposes.

- **apiInfo()**: `ApiInfo`
  - **Summary**: This method generates an ApiInfo instance that holds essential metadata about the API to be displayed in the Swagger UI interface, such as title, description, contact details, license information, and additional documentation links.
  - **External Calls**:
    - `Collections.`emptyList()` is called within this method to create a list of supported media types for response content negotiation (e.g., JSON, XML). This empty list indicates that there are no specific media type preferences in the API documentation generated by Swagger UI.

```markdown
---
title: "SpringDataCassandraApplication"
description: |
The SpringDataCassandraApplication class serves as a bridge between Java applications and Apache Cassandra using the DataStax driver, configured with secure connect bundles via Spring Boot.
package_path: "/com/datastax/examples/SpringDataCassandraApplication.java"
responsibility: "Provides an entry point for running a Spring Boot application that integrates with Apache Cassandra using secure connections."
---

## Fields
(No fields are defined in the JSON metadata)

## Methods

### main()
**Type:** `void`  
This method is the application's entry point. It starts a Spring Boot application and runs it with the class itself as the source of configuration.
- **External Calls**:
  - `SpringApplication.run(SpringDataCassandraApplication.class, args)` to start the Spring Boot application using the current class as its primary configuration class and passing any command-line arguments received.

### sessionBuilderCustomizer()
**Type:** `CqlSessionBuilderCustomizer`  
This method customizes the CQL session builder by adding a secure connect bundle if available, which is used to establish connections with Cassandra clusters via secure transport protocols.
- **External Calls**:
  - `DataStaxAstraProperties.getSecureConnectBundle()` to retrieve the secure connect bundle configuration defined in external properties files or application configurations.
  - `DataStaxAstraProperties.toPath()` to convert the secure connect bundle into a file path representation that can be used with the session builder.
  - `builder.withCloudSecureConnectBundle(bundle)` to apply the secure connect bundle configuration to the CqlSessionBuilder, enabling secure connections when establishing communication with Cassandra clusters.
```

```markdown
---
title: "DataStaxAstraProperties"
class_name: "DataStaxAstraProperties"
package: "com.datastax.examples"
file_path: "src/main/java/com/datastax/examples/DataStaxAstraProperties.java"
module: "root"
summary: "[Brief description of what the class does]"
fields: 
  - name: "File"
    type: "secureConnectBundle"
    dependency: None
functions: []

## Package
`com.datastax.examples`

## File Path
`src/main/java/com/datastax/examples/DataStaxAstraProperties.java`

## Responsibility
The `DataStaxAstraProperties` class is responsible for storing and managing configuration properties related to the secure connect bundle in a DataStax Astra application.

## Fields
* **File**: `secureConnectBundle` (type: File, dependency: None)
  * This field holds the path to the Secure Connect Bundle file used by the application for authentication with an external Cassandra cluster.
```
