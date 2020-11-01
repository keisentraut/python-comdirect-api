import datetime
import io


def is_alphanum(c):
    ALPHANUM = set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,-äüöÄÜÖß")
    return c in ALPHANUM


def make_printable(s):
    return "".join([i if is_alphanum(i) else "_" for i in s])


def timestamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S%f")


def is_valid_TAN(tan):
    return type(tan) == str and len(tan) == 6 and set(tan) <= set("0123456789")


def default_callback_p_tan(pngImage):
    from PIL import Image

    Image.open(io.BytesIO(pngImage)).show()
    p_tan = input("Please enter Photo-TAN: ")
    if not is_valid_TAN(p_tan):
        raise ValueError(f"invalid Photo-TAN {p_tan}")
    return p_tan


def default_callback_m_tan():
    m_tan = input("Please enter your SMS-TAN: ")
    if not is_valid_TAN(m_tan):
        raise ValueError(f"invalid SMS-TAN {m_tan}")
    return m_tan


def default_callback_p_tan_push():
    m_tan = input("Please press ENTER after confirming push-tan ")
    m_tan = "123456"
    return m_tan
