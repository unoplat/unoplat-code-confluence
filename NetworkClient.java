/**
 * This class, NetworkClient, is used to fetch data from a specific URL and print it.
 * It uses an instance of NetworkService to fetch the data.
 */
public class NetworkClient {
    
    // Declaring a private instance of NetworkService
    private NetworkService networkService;
    
    // Constructor for NetworkClient that takes a NetworkService object as an argument
    public NetworkClient(NetworkService networkService) {
        // Assigning the networkService argument to the instance variable
        this.networkService = networkService;
    }

    // Method that fetches data from a given URL and prints it
    public void fetchDataAndPrint(String url) {
        // Printing the URL from which data is being fetched
        System.out.println("Fetching data from: " + url);
        // Fetching the data and storing it in a string
        String result = networkService.fetchData(url);
        // Printing the fetched data
        System.out.println("Received: " + result);
    }

    // Main method
    public static void main(String[] args) {
        // Creating a new instance of SimpleNetworkService
        NetworkService service = new SimpleNetworkService();
        // Creating a new instance of NetworkClient and passing the service object to its constructor
        NetworkClient client = new NetworkClient(service);
        // Fetching and printing data from a specific URL
        client.fetchDataAndPrint("http://example.com/api/data");
    }
}
