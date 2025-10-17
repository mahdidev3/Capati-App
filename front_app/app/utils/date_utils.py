"""
Date and time utilities for converting to Jalali calendar and Iran timezone
"""

# Try to import optional packages
try:
    import jdatetime
    import pytz
    from datetime import datetime

    DATE_UTILS_AVAILABLE = True
except ImportError as e:
    DATE_UTILS_AVAILABLE = False
    jdatetime = None
    pytz = None
    datetime = None


def to_jalali(dt_str, include_time=True):
    """Convert a datetime string to Jalali (Persian) calendar with Iran timezone"""
    if dt_str is None or dt_str == '':
        return '-'

    # Parse the string to datetime
    try:
        # Assuming input format is something like 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00')) if '+' in dt_str or 'Z' in dt_str else datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S' if ' ' in dt_str else '%Y-%m-%d')
    except (ValueError, TypeError):
        return dt_str  # Return original string if parsing fails

    # If date utilities not available, return Gregorian date
    if not DATE_UTILS_AVAILABLE:
        if include_time:
            return dt.strftime('%Y/%m/%d - %H:%M')
        else:
            return dt.strftime('%Y/%m/%d')

    try:
        # Convert to Iran timezone
        if dt.tzinfo is None:
            # Assume UTC if no timezone info
            dt = pytz.UTC.localize(dt)

        iran_tz = pytz.timezone('Asia/Tehran')
        dt_iran = dt.astimezone(iran_tz)

        # Convert to Jalali
        jalali_date = jdatetime.datetime.fromgregorian(datetime=dt_iran)

        if include_time:
            return jalali_date.strftime('%Y/%m/%d - %H:%M')
        else:
            return jalali_date.strftime('%Y/%m/%d')
    except Exception as e:
        # Fallback to Gregorian
        if include_time:
            return dt.strftime('%Y/%m/%d - %H:%M')
        else:
            return dt.strftime('%Y/%m/%d')


def setup_jinja_filters(app):
    """Register Jinja2 filters for date formatting"""

    @app.template_filter('jalali')
    def jalali_filter(dt_str):
        """Jinja2 filter for converting datetime string to Jalali with time"""
        try:
            return to_jalali(dt_str, include_time=True)
        except Exception as e:
            # Parse string to datetime for fallback
            try:
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00')) if '+' in dt_str or 'Z' in dt_str else datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S' if ' ' in dt_str else '%Y-%m-%d')
                return dt.strftime('%Y/%m/%d - %H:%M')
            except (ValueError, TypeError):
                return dt_str if dt_str else '-'

    @app.template_filter('jalali_date')
    def jalali_date_filter(dt_str):
        """Jinja2 filter for converting datetime string to Jalali date only"""
        try:
            return to_jalali(dt_str, include_time=False)
        except Exception as e:
            # Parse string to datetime for fallback
            try:
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00')) if '+' in dt_str or 'Z' in dt_str else datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S' if ' ' in dt_str else '%Y-%m-%d')
                return dt.strftime('%Y/%m/%d')
            except (ValueError, TypeError):
                print(dt_str)
                return dt_str if dt_str else '-'

    @app.template_filter('jalali_time')
    def jalali_time_filter(dt_str):
        """Jinja2 filter for extracting time in Iran timezone"""
        if dt_str is None or dt_str == '':
            return '-'

        # Parse string to datetime
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00')) if '+' in dt_str or 'Z' in dt_str else datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S' if ' ' in dt_str else '%Y-%m-%d')
        except (ValueError, TypeError):
            return dt_str  # Return original string if parsing fails

        if not DATE_UTILS_AVAILABLE:
            return dt.strftime('%H:%M')

        try:
            # Convert to Iran timezone
            if dt.tzinfo is None:
                dt = pytz.UTC.localize(dt)

            iran_tz = pytz.timezone('Asia/Tehran')
            dt_iran = dt.astimezone(iran_tz)

            return dt_iran.strftime('%H:%M')
        except Exception as e:
            return dt.strftime('%H:%M')