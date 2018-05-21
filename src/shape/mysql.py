import hmac
import aiomysql
import bcrypt


def constant_time_compare(val1, val2):
    """Return True if the two strings are equal, False otherwise."""
    return hmac.compare_digest(val1, val2)


class BlowfishPasswordHasher:
    """Secure password hashing using the blowfish algorithm.

    Needs the bcrypt library.  Please be warned that
    this library depends on native C code and might cause portability
    issues.

    This is compatible with PHP's CRYPT_BLOWFISH (prefix is '$2y$').

    """
    algorithm = 'bcrypt_php'
    rounds = 10

    def salt(self):
        return b'$2y$' + bcrypt.gensalt(self.rounds)[4:]

    def encode(self, password, salt):
        return bcrypt.hashpw(password, salt)

    def verify(self, password, encoded):
        assert encoded.startswith(b'$2y$')
        encoded_2 = self.encode(password, encoded)
        return constant_time_compare(encoded, encoded_2)


class DataStore:
    def __init__(self, options):
        self.options = options
        self.jwt_by_jids = {}

    async def on_startup(self, app):
        self.pool = await aiomysql.create_pool(
            host=self.options.get('host', '127.0.0.1'),
            port=self.options.get('port', 3306),
            user=self.options.get('user', 'root'),
            password=self.options.get('password', ''),
            db=self.options.get('database', 'test'))

    async def on_cleanup(self, app):
        self.pool.close()
        await self.pool.wait_closed()

    async def identify(self, login, password):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    "SELECT * FROM system2_info where login = %s",
                    (login, ))
                user = await cur.fetchone()
        if BlowfishPasswordHasher().verify(password.encode('utf8'),
                                           user['password'].encode('utf8')):
            return user
        return None
