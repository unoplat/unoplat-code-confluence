"""Module for testing instance variable edge cases."""

# Global variables (should be excluded from class variables)
GLOBAL_CONFIG = {"debug": True}
app_instance = None


class FastAPIApp:
    """FastAPI application class with various instance variable patterns."""

    # Direct class variables (should be captured)
    CLASS_CONSTANT = "production"
    shared_cache: dict = {}

    def __init__(self, config: dict):
        """Initialize with comprehensive instance variable patterns."""

        # Basic instance variables (should be captured)
        self.app = FastAPI()
        self.config = config
        self.database_url: str = config.get("db_url", "")

        # Type-annotated instance variables (should be captured)
        self.clients: List[HttpClient] = []
        self.cache: Optional[RedisCache] = None
        self.metrics: Dict[str, int] = {}

        # Complex expressions as values (should be captured)
        self.router = APIRouter(prefix="/api/v1")
        self.middleware_stack = [
            CORSMiddleware,
            SecurityMiddleware(api_key=config["api_key"]),
        ]

        # Conditional assignment (should be captured if in expression_statement)
        if config.get("enable_auth", False):
            self.auth_handler = AuthHandler(config["auth_config"])
        else:
            self.auth_handler = None

        # Nested attribute assignment (should be captured)
        self.settings.debug = config.get("debug", False)
        self.settings.timeout = 30

        # Method call results (should be captured)
        self.connection = self._create_connection()
        self.logger = setup_logger(config.get("log_level", "INFO"))

        # Multiple assignments on same line (edge case)
        self.host, self.port = config.get("host", "localhost"), config.get("port", 8000)

        # F-string and complex string formatting (should be captured)
        self.base_url = f"https://{self.host}:{self.port}"
        self.version_info = f"App v{config.get('version', '1.0')}"

        # Lambda and comprehension assignments (should be captured)
        self.data_processor = lambda x: x.strip().lower()
        self.valid_routes = [
            route for route in config.get("routes", []) if route.startswith("/")
        ]

        # Dictionary and list literals (should be captured)
        self.response_headers = {
            "Content-Type": "application/json",
            "X-API-Version": "1.0",
        }
        self.supported_methods = ["GET", "POST", "PUT", "DELETE"]

    def configure_middleware(self):
        """Method with instance variable assignments (should be captured)."""

        # Instance variables in regular methods (should be captured)
        self.cors_middleware = CORSMiddleware(allow_origins=["*"], allow_methods=["*"])
        self.rate_limiter = RateLimiter(requests_per_minute=100)

        # Local variables in methods (should NOT be captured)
        local_config = {"temp": True}
        middleware_list = []
        temp_handler = TemporaryHandler()

        # Method calls on self (instance variables should be captured)
        self.security_config = self._get_security_config()

        # Assignment to non-self variables (should NOT be captured)
        other_obj = SomeOtherClass()
        other_obj.config = {"external": True}
        different.setting = "value"

        # Complex self attribute chains (should be captured)
        self.nested.handler.config = {"nested": True}
        self.deep.very.nested.setting = "deep_value"

    @staticmethod
    def create_default_config():
        """Static method with no instance variables."""
        # Local variables in static methods (should NOT be captured)
        default_settings = {"mode": "default"}
        temp_config = {}
        return default_settings

    @classmethod
    def from_config_file(cls, config_path: str):
        """Class method with local variables (should NOT be captured)."""
        # Local variables in class methods (should NOT be captured)
        config_data = load_config(config_path)
        instance = cls(config_data)
        return instance

    def _create_connection(self):
        """Private method with nested function containing instance variables."""

        # Instance variable in private method (should be captured)
        self.connection_pool = ConnectionPool()

        # Nested function with its own variables (should NOT affect instance vars)
        def inner_connection_helper():
            # Local variables in nested function (should NOT be captured)
            local_conn = create_local_connection()
            helper_config = {"helper": True}

            # Even if it looks like instance variable, it's in nested scope
            # (This should NOT be captured as instance variable)
            inner_self = MockSelf()
            inner_self.fake_attr = "not_real_instance_var"

            return local_conn

        # Instance variable after nested function (should be captured)
        self.connection_helper = inner_connection_helper

        return inner_connection_helper()

    async def async_setup(self):
        """Async method with instance variables (should be captured)."""

        # Instance variables in async methods (should be captured)
        self.async_client = AsyncHttpClient()
        self.event_loop = asyncio.get_event_loop()

        # Await expressions (should be captured)
        self.async_data = await self.fetch_initial_data()

        # Local variables in async method (should NOT be captured)
        async_config = {"async": True}
        await asyncio.sleep(0.1)


class NestedClassTest:
    """Test class with nested class containing instance variables."""

    # Class variable (should be captured)
    PARENT_CONSTANT = "parent"

    def __init__(self):
        # Parent instance variables (should be captured)
        self.parent_attr = "parent_value"
        self.nested_instance = self.NestedClass()

    class NestedClass:
        """Nested class with its own instance variables."""

        # Nested class variable (should be captured for NestedClass)
        NESTED_CONSTANT = "nested"

        def __init__(self):
            # Nested class instance variables (should be captured for NestedClass)
            self.nested_attr = "nested_value"
            self.config = {"nested": True}


class TypeAnnotatedClass:
    """Class with comprehensive type annotations."""

    # Annotated class variables (should be captured)
    class_config: ClassVar[Dict[str, str]] = {"global": "config"}
    shared_state: ClassVar[List[str]] = []

    def __init__(self, data: Dict[str, Any]):
        # Type-annotated instance variables (should be captured)
        self.typed_config: Dict[str, Any] = data
        self.optional_cache: Optional[CacheType] = None
        self.generic_list: List[GenericType[T]] = []
        self.union_type: Union[str, int, None] = None
        self.complex_type: Dict[str, List[Optional[CustomType]]] = {}


class PropertyAndDescriptorClass:
    """Class with properties and descriptors that might confuse the parser."""

    # Class variable (should be captured)
    DEFAULT_VALUE = "default"

    def __init__(self):
        # Instance variables (should be captured)
        self._private_value = "private"
        self.public_value = "public"

    @property
    def computed_value(self):
        """Property that doesn't create instance variables."""
        # Local variables in properties (should NOT be captured)
        temp_calc = self._private_value.upper()
        return temp_calc

    @computed_value.setter
    def computed_value(self, value):
        """Property setter."""
        # Instance variable in setter (should be captured)
        self._private_value = value

        # Local variable in setter (should NOT be captured)
        validation_result = validate(value)


def module_level_function():
    """Module function that should not affect class variable detection."""
    # Local variables (should NOT be captured)
    local_var = "local"
    fake_self = FakeClass()
    fake_self.attribute = "not_instance_var"

    # Nested function
    def nested():
        nested_var = "nested"
        return nested_var

    return nested()


# More global variables (should be excluded from class variables)
ANOTHER_GLOBAL = "global"
module_config = {"module": True}
