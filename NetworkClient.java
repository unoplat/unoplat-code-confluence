/**
 * NetworkClient class that handles network operations.
 */
public class NetworkClient {

    /**
     * Private instance of NetworkService.
     */
    private NetworkService networkService;

    /**
     * Constructor for NetworkClient that takes a NetworkService object as an argument.
     *
     * @param networkService The network service to be used with this client.
     */
    public NetworkClient(NetworkService networkService) {
        // Assigning the networkService argument to the instance variable
        this.networkService = networkService;
    }

    /**
     * Fetches data from a specified URL and prints it.
     *
     * @param url The URL from which data is fetched.
     */
    public void fetchDataAndPrint(String url) {
        // Printing the URL from which data is being fetched
        System.out.println("Fetching data from: " + url);
        // Fetching the data and storing it in a string
        String result = networkService.fetchData(url);
        // Printing the fetched data
        System.out.println("Received: " + result);
    }

    /**
     * Main method to run the NetworkClient example.
     *
     * @param args Command line arguments (not used).
     */
    public static void main(String[] args) {
        // Creating a new instance of SimpleNetworkService
        NetworkService service = new SimpleNetworkService();
        // Creating a new instance of NetworkClient and passing the service object to its constructor
        NetworkClient client = new NetworkClient(service);
        // Fetching and printing data from a specific URL
        client.fetchDataAndPrint("http://example.com/api/data");
    }
}
