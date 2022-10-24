from django.db import models

# Create your models here.


# class SettingGroups(models.Model):
#     id = models.AutoField(primary_key=True)
#     setting_type = models.CharField(max_length=255, blank=True, null=True)
#     setting_name = models.CharField(max_length=255, blank=True, null=True)
#     created_at = models.DateTimeField()
#     updated_at = models.DateTimeField()

#     def __str__(self):
#         if self.setting_name:
#             return self.setting_name
#         else:
#             return ""

#     class Meta:
#         managed = False
#         db_table = "setting_groups"
#         verbose_name = "Setting Group"
#         verbose_name_plural = "Setting Groups"


class AccountProviders(models.Model):
    id = models.AutoField(primary_key=True)
    account_id = models.IntegerField(blank=True, null=True)
    provider_type = models.CharField(max_length=255, blank=True, null=True)
    provider_value = models.CharField(max_length=255, blank=True, null=True)
    provider_key = models.TextField(blank=True, null=True)
    reset_key = models.CharField(max_length=255, blank=True, null=True)
    reset_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "account_providers"
        verbose_name = "Account Provider"
        verbose_name_plural = "Account Providers"


class Accounts(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    account_token = models.CharField(max_length=255, blank=True, null=True)
    photo_file_name = models.CharField(max_length=255, blank=True, null=True)
    photo_content_type = models.CharField(max_length=255, blank=True, null=True)
    photo_file_size = models.IntegerField(blank=True, null=True)
    photo_updated_at = models.DateTimeField(blank=True, null=True)
    locale = models.CharField(max_length=255, blank=True, null=True)
    api_version = models.CharField(max_length=255, blank=True, null=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    unsubscribed = models.IntegerField(blank=True, null=True)
    unsubscribe_key = models.CharField(max_length=255, blank=True, null=True)
    using_geolocation = models.IntegerField(blank=True, null=True)
    last_longitude = models.FloatField(blank=True, null=True)
    last_latitude = models.FloatField(blank=True, null=True)
    app_name = models.CharField(max_length=255, blank=True, null=True)
    app_platform = models.CharField(max_length=255, blank=True, null=True)
    banned = models.IntegerField(blank=True, null=True)
    last_email_sent = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "accounts"
        verbose_name = "Account"
        verbose_name_plural = "Accounts"


class ArInternalMetadata(models.Model):
    key = models.CharField(primary_key=True, max_length=255)
    value = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "ar_internal_metadata"
        verbose_name = "Ar Internal Metadata"
        verbose_name_plural = "Ar Internat Metadata"


class Joyns(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.CharField(max_length=255, blank=True, null=True)
    product_name = models.TextField(blank=True, null=True)
    custom1 = models.TextField(blank=True, null=True)
    custom2 = models.TextField(blank=True, null=True)
    custom3 = models.TextField(blank=True, null=True)
    product_short_description = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    product_type = models.TextField(blank=True, null=True)
    specifications = models.TextField(blank=True, null=True)
    primary_artist = models.TextField(blank=True, null=True)
    custom4 = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    language = models.TextField(blank=True, null=True)
    custom5 = models.TextField(blank=True, null=True)
    custom6 = models.TextField(blank=True, null=True)
    merchant_category = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    merchant_thumb = models.TextField(blank=True, null=True)
    deep_link = models.TextField(blank=True, null=True)
    stock_status = models.TextField(blank=True, null=True)
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_to = models.DateTimeField(blank=True, null=True)
    contract_type = models.TextField(blank=True, null=True)
    delivery_restrictions = models.TextField(blank=True, null=True)
    custom7 = models.TextField(blank=True, null=True)
    custom8 = models.IntegerField(blank=True, null=True)
    dimensions = models.TextField(blank=True, null=True)
    custom9 = models.TextField(blank=True, null=True)
    time = models.IntegerField(blank=True, null=True)
    parent_product_id = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "joyns"
        verbose_name = "Joyn"
        verbose_name_plural = "Joyns"


class Keywords(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    tmdb_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "keywords"
        verbose_name = "Keyword"
        verbose_name_plural = "Keywords"


class KeywordsMovies(models.Model):
    id = models.AutoField(primary_key=True)
    keyword_id = models.IntegerField(blank=True, null=True)
    movie_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "keywords_movies"
        verbose_name = "Keywords Movie"
        verbose_name_plural = "Keywords Movies"


class Logs(models.Model):
    id = models.AutoField(primary_key=True)
    account_id = models.IntegerField(blank=True, null=True)
    event_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user_id = models.IntegerField(blank=True, null=True)
    event_description = models.TextField(blank=True, null=True)
    event_key = models.CharField(max_length=255, blank=True, null=True)
    event_value = models.CharField(max_length=255, blank=True, null=True)
    cinema_id = models.IntegerField(blank=True, null=True)
    chain_id = models.IntegerField(blank=True, null=True)
    info_id = models.IntegerField(blank=True, null=True)
    movie_id = models.IntegerField(blank=True, null=True)
    tv_show_translation_id = models.IntegerField(blank=True, null=True)
    push_notification_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "logs"
        verbose_name = "Log"
        verbose_name_plural = "Logs"


class NotificationLogs(models.Model):
    id = models.AutoField(primary_key=True)
    notification_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    account_id = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    last_view_at = models.DateTimeField(blank=True, null=True)
    last_user_action = models.CharField(max_length=255, blank=True, null=True)
    impressions = models.IntegerField(blank=True, null=True)
    clicks = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "notification_logs"
        verbose_name = "Notification Log"
        verbose_name_plural = "Notification Logs"


class Notifications(models.Model):
    id = models.AutoField(primary_key=True)
    action_type = models.CharField(max_length=255, blank=True, null=True)
    action_value = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    locale = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=255, blank=True, null=True)
    users_type = models.CharField(max_length=255, blank=True, null=True)
    condition_type = models.CharField(max_length=255, blank=True, null=True)
    condition_value = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    photo_file_name = models.CharField(max_length=255, blank=True, null=True)
    photo_content_type = models.CharField(max_length=255, blank=True, null=True)
    photo_file_size = models.IntegerField(blank=True, null=True)
    photo_updated_at = models.DateTimeField(blank=True, null=True)
    repeat_type = models.CharField(max_length=255, blank=True, null=True)
    repeat_value = models.IntegerField(blank=True, null=True)
    notification_type = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    status_type = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    radius = models.FloatField(blank=True, null=True)
    ad_56_portrait_file_name = models.CharField(max_length=255, blank=True, null=True)
    ad_56_portrait_content_type = models.CharField(
        max_length=255, blank=True, null=True
    )
    ad_56_portrait_file_size = models.IntegerField(blank=True, null=True)
    ad_56_portrait_updated_at = models.DateTimeField(blank=True, null=True)
    ad_75_portrait_file_name = models.CharField(max_length=255, blank=True, null=True)
    ad_75_portrait_content_type = models.CharField(
        max_length=255, blank=True, null=True
    )
    ad_75_portrait_file_size = models.IntegerField(blank=True, null=True)
    ad_75_portrait_updated_at = models.DateTimeField(blank=True, null=True)
    ad_75_landscape_file_name = models.CharField(max_length=255, blank=True, null=True)
    ad_75_landscape_content_type = models.CharField(
        max_length=255, blank=True, null=True
    )
    ad_75_landscape_file_size = models.IntegerField(blank=True, null=True)
    ad_75_landscape_updated_at = models.DateTimeField(blank=True, null=True)
    max_impressions = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "notifications"
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"


class PassbookRegistrations(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=255, blank=True, null=True)
    device_id = models.CharField(max_length=255, blank=True, null=True)
    push_token = models.CharField(max_length=255, blank=True, null=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True)
    pass_type_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "passbook_registrations"
        verbose_name = "Passbook Registration"
        verbose_name_plural = "Passbook Registrations"


class Passes(models.Model):
    id = models.AutoField(primary_key=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True)
    authentication_token = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    ticket_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "passes"
        verbose_name = "Pass"
        verbose_name_plural = "Passes"


class PushNotifications(models.Model):
    id = models.AutoField(primary_key=True)
    push_platform = models.CharField(max_length=255, blank=True, null=True)
    push_type = models.CharField(max_length=255, blank=True, null=True)
    info_ids = models.CharField(max_length=255, blank=True, null=True)
    tv_show_translation_ids = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    badge = models.IntegerField(blank=True, null=True)
    push_at = models.DateTimeField(blank=True, null=True)
    user_ids = models.TextField(blank=True, null=True)
    prepared_ids = models.TextField(blank=True, null=True)
    sent_ids = models.TextField(blank=True, null=True)
    open_ids = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    permanent = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "push_notifications"
        verbose_name = "Push Notification"
        verbose_name_plural = "Push Notifications"


class QrCodes(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    image_file_name = models.CharField(max_length=255, blank=True, null=True)
    image_content_type = models.CharField(max_length=255, blank=True, null=True)
    image_file_size = models.IntegerField(blank=True, null=True)
    image_updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "qr_codes"
        verbose_name = "QR Code"
        verbose_name_plural = "QR Codes"


class Reminders(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(blank=True, null=True)
    account_id = models.IntegerField(blank=True, null=True)
    info_id = models.IntegerField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    pushed = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    app_platform = models.CharField(max_length=255, blank=True, null=True)
    app_name = models.CharField(max_length=255, blank=True, null=True)
    push_token = models.TextField(blank=True, null=True)
    reminder_type = models.CharField(max_length=255, blank=True, null=True)
    push_later = models.IntegerField(blank=True, null=True)
    locale = models.CharField(max_length=255, blank=True, null=True)
    text = models.CharField(max_length=255, blank=True, null=True)
    did_open = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "reminders"
        verbose_name = "Reminder"
        verbose_name_plural = "Reminders"


class ScreenLogs(models.Model):
    id = models.AutoField(primary_key=True)
    cinema_id = models.IntegerField(blank=True, null=True)
    screen_id = models.IntegerField(blank=True, null=True)
    info_id = models.IntegerField(blank=True, null=True)
    showtime_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    occupied_seat_ids = models.TextField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    account_id = models.IntegerField(blank=True, null=True)
    chain_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "screen_logs"
        verbose_name = "Screen Log"
        verbose_name_plural = "Screen Logs"


class Screens(models.Model):
    id = models.AutoField(primary_key=True)
    cinema_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    cinema_screen_id = models.CharField(max_length=255, blank=True, null=True)
    row_order = models.IntegerField(blank=True, null=True)
    column_order = models.IntegerField(blank=True, null=True)
    row_naming = models.IntegerField(blank=True, null=True)
    column_naming = models.IntegerField(blank=True, null=True)
    id_row_order = models.IntegerField(blank=True, null=True)
    id_column_order = models.IntegerField(blank=True, null=True)
    id_row_naming = models.IntegerField(blank=True, null=True)
    id_column_naming = models.IntegerField(blank=True, null=True)
    seating_option_allow_single_space = models.IntegerField(blank=True, null=True)
    seating_option_can_split_double_seats = models.IntegerField(blank=True, null=True)
    json_field = models.TextField(blank=True, null=True)
    row_names_overwrite = models.TextField(blank=True, null=True)
    column_names_overwrite = models.TextField(blank=True, null=True)
    row_ids_overwrite = models.TextField(blank=True, null=True)
    column_ids_overwrite = models.TextField(blank=True, null=True)
    video_system = models.CharField(max_length=255, blank=True, null=True)
    capacity = models.CharField(max_length=255, blank=True, null=True)
    photo_file_name = models.CharField(max_length=255, blank=True, null=True)
    photo_content_type = models.CharField(max_length=255, blank=True, null=True)
    photo_file_size = models.IntegerField(blank=True, null=True)
    photo_updated_at = models.DateTimeField(blank=True, null=True)
    audio_system = models.CharField(max_length=255, blank=True, null=True)
    display_size = models.CharField(max_length=255, blank=True, null=True)
    default_area_code = models.CharField(max_length=255, blank=True, null=True)
    parser_data = models.TextField(blank=True, null=True)
    parser_type = models.CharField(max_length=255, blank=True, null=True)
    seating_option_allow_single_space_to_loveseat = models.IntegerField(
        blank=True, null=True
    )
    auto_count_on_edit = models.IntegerField(blank=True, null=True)
    parsing_options = models.TextField(blank=True, null=True)
    free_seating = models.IntegerField(blank=True, null=True)
    seating_option_prefer_empty_at_row_end_or_left = models.IntegerField(
        blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "screens"
        verbose_name = "Screen"
        verbose_name_plural = "Screens"


class Seats(models.Model):
    id = models.AutoField(primary_key=True)
    draw_x = models.IntegerField(blank=True, null=True)
    draw_y = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    screen_id = models.IntegerField(blank=True, null=True)
    row = models.CharField(max_length=255, blank=True, null=True)
    column = models.CharField(max_length=255, blank=True, null=True)
    cinema_seat_id = models.CharField(max_length=255, blank=True, null=True)
    seat_type = models.IntegerField(blank=True, null=True)
    draw_type = models.IntegerField(blank=True, null=True)
    skip_id = models.IntegerField(blank=True, null=True)
    skip_name = models.IntegerField(blank=True, null=True)
    cant_select = models.IntegerField(blank=True, null=True)
    save_for_undo = models.IntegerField(blank=True, null=True)
    area_code = models.CharField(max_length=255, blank=True, null=True)
    area_type = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "seats"
        verbose_name = "Seat"
        verbose_name_plural = "Seats"


class Settings(models.Model):
    id = models.AutoField(primary_key=True)
    # setting_group_id = models.IntegerField(blank=True, null=True)
    key = models.CharField(max_length=255, blank=True, null=True)
    value = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "settings"
        verbose_name = "Setting"
        verbose_name_plural = "Settings"


class Tickets(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    account_id = models.IntegerField(blank=True, null=True)
    info_id = models.IntegerField(blank=True, null=True)
    movie_title = models.CharField(max_length=255, blank=True, null=True)
    cinema_id = models.IntegerField(blank=True, null=True)
    cinema_screen_id = models.CharField(max_length=255, blank=True, null=True)
    reservation_code = models.CharField(max_length=255, blank=True, null=True)
    selected_seats = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    price = models.CharField(max_length=255, blank=True, null=True)
    holder = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    selected_seat_ids = models.CharField(max_length=255, blank=True, null=True)
    showtime_value = models.CharField(max_length=255, blank=True, null=True)
    screen_id = models.IntegerField(blank=True, null=True)
    number_of_seats = models.IntegerField(blank=True, null=True)
    movie_id = models.IntegerField(blank=True, null=True)
    ticket_type = models.CharField(max_length=255, blank=True, null=True)
    booking_type = models.CharField(max_length=255, blank=True, null=True)
    payment_type = models.CharField(max_length=255, blank=True, null=True)
    convenience_fee = models.CharField(max_length=255, blank=True, null=True)
    account_connection_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    chain_id = models.IntegerField(blank=True, null=True)
    qr_code_id = models.IntegerField(blank=True, null=True)
    hash_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "tickets"
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"


class Users(models.Model):
    id = models.AutoField(primary_key=True)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    locale = models.CharField(max_length=255, blank=True, null=True)
    api_version = models.CharField(max_length=255, blank=True, null=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    account_id = models.IntegerField(blank=True, null=True)
    os_version = models.CharField(max_length=255, blank=True, null=True)
    app_version = models.CharField(max_length=255, blank=True, null=True)
    using_geolocation = models.IntegerField(blank=True, null=True)
    push_token = models.TextField(blank=True, null=True)
    push_device = models.CharField(max_length=255, blank=True, null=True)
    push_last_date = models.DateTimeField(blank=True, null=True)
    ip_address = models.TextField(blank=True, null=True)
    app_name = models.CharField(max_length=255, blank=True, null=True)
    app_platform = models.CharField(max_length=255, blank=True, null=True)
    banned = models.IntegerField(blank=True, null=True)
    last_latitude = models.FloatField(blank=True, null=True)
    last_longitude = models.FloatField(blank=True, null=True)
    last_email_sent_on = models.DateTimeField(blank=True, null=True)
    last_services = models.CharField(max_length=255, blank=True, null=True)
    tester = models.IntegerField(blank=True, null=True)
    phone_version = models.CharField(max_length=255, blank=True, null=True)
    was_signed_in = models.IntegerField(blank=True, null=True)
    kinode_favorites = models.TextField(blank=True, null=True)
    developer = models.IntegerField(blank=True, null=True)
    supporter = models.IntegerField(blank=True, null=True)
    aws_sns_endpoint_arn = models.CharField(max_length=255, blank=True, null=True)
    sandbox_token = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"


class Watchlists(models.Model):
    id = models.AutoField(primary_key=True)
    movie_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user_id = models.IntegerField(blank=True, null=True)
    account_id = models.IntegerField(blank=True, null=True)
    locale = models.CharField(max_length=255, blank=True, null=True)
    info_id = models.IntegerField(blank=True, null=True)
    tv_show_translation_id = models.IntegerField(blank=True, null=True)
    stars = models.FloatField(blank=True, null=True)
    review = models.TextField(blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    trailer_watched_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "watchlists"
        verbose_name = "Watchlist"
        verbose_name_plural = "Watchlists"


class Admins(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password_hash = models.CharField(max_length=255, blank=True, null=True)
    salt = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    locale = models.CharField(max_length=255, blank=True, null=True)
    api_key = models.TextField(blank=True, null=True)
    api_key_date = models.DateTimeField()
    api_request_count = models.IntegerField(blank=True, null=True)
    api_request_last_date = models.DateTimeField()

    def __str__(self):
        if self.username:
            return self.username
        else:
            return ""

    class Meta:
        managed = False
        db_table = "admins"
        verbose_name = "Admin"
        verbose_name_plural = "Admins"
