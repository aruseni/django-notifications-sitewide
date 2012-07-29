django-notifications-sitewide
=============================

django-notifications-sitewide allows you to show site-wide notifications to inform your users about maintenance and other important events (one at a time).

# Features

* Store as many notifications as you want, show one at a time
* The shown notification is cached, so it doesn’t use the database until the cache items expire
* If there is no active notification (which is very common), this state is cached too
* Each user can close (hide) the currently shown notification
* If you edit the notification (correct typos, etc), it remains hidden for those users who closed it
* If you create a new notification (or disable, and then enable a previously shown), then it is shown for all users (whether they hid the previous notification or not)
* The installation process is clean and easy

The notification is shown on every page until the user clicks the ×:

![Notification shown (screenshot)](http://dl.dropbox.com/u/17482399/django-notifications-sitewide-notification_shown.png)

As soon as the user clicks ×, the notification is hidden (but an icon appears, and it allows to show the notification again):

![Notification hidden (screenshot)](http://dl.dropbox.com/u/17482399/django-notifications-sitewide-notification_hidden.png)

# How it works

After you installed the reusable application (it’s called “notifications”), you can go to the admin site and add a notification. If you check the “Show on the website” checkbox, the notification is marked as active: the show_this_message field is set to True and the shown_since field is populated with the current date and time. All other notifications are updated to make certain that these fields are only set for this notification (as there cannot be more than one shown notification at a time). The same also happens if you save a previously created notification object.

Every time you save or delete a notification, the “shown_notification” key is deleted from the cache and the “shown_notification_available” cache key is set to True if there is a notification with the show_this_message set to True (otherwise the cache key is set to False).

When a user opens a page, the [context processor](https://docs.djangoproject.com/en/dev/ref/templates/api/#subclassing-context-requestcontext) checks the “shown_notification_available” cache key. If it is set to False, then it only returns None as the notification:

    {'top_notification': None}

If the “shown_notification_available” cache key is not present, or is set to True, then it tries to load the notification object from the cache (using the “shown_notification” cache key).

If there is no such item in the cache, then it tries to load it from the database. If it’s not in the database either, the “shown_notification_available” cache key is set to False (so the context processor won’t try to load it from the database next time: until the cache item expires or a site administrator creates a shown notification).

If the notification is found in the database, it is written to the “shown_notification” cache key.

In case the notification is available (whereever it was loaded from), it is included into the context and the request.COOKIES dictionary is checked. If it has the “closed_notification_timestamp” and the timestamp equals to the timestamp from the shown_since field of the notification, then the context processor sets the “hide_top_notification” context variable to True. Otherwise it is set to False.

Then, if there is an active notification, it is shown on the website. If the hide_top_notification context variable is set to True, then the notification is hidden by default, but an icon is shown (and the user can click on it and the notification appears). It hide_top_notification it set to False, then the icon used to show the notification is hidden by default, but the notification itself is shown.

When the user clicks the ×, the notification is hidden (and the icon for showing it again appears), and the “closed_notification_timestamp” cookie is set to the timestamp of the shown notification (taken from the “timestamp” data attribute of the div tag that contains the notification).

# Installation

#### Step 1
Clone this repository:

    git clone git://github.com/aruseni/django-notifications-sitewide.git

#### Step 2
Put the “notifications” reusable application somewhere on your PYTHONPATH (e.g. in your project directory).

#### Step 3
Open settings.py for your project.

#### Step 4
Add the application to INSTALLED_APPS:

    INSTALLED_APPS = (
        …
        'notifications',
        …
    )

#### Step 5
Add the context processor:

    TEMPLATE_CONTEXT_PROCESSORS = (
        …
        "notifications.context_processors.notification_processor",
        …
    )

**Note**: if you didn’t add any context processors before (you don’t have TEMPLATE_CONTEXT_PROCESSORS in your settings.py), make sure to also [specify the default ones](https://docs.djangoproject.com/en/1.1/ref/settings/#template-context-processors) so they continue to work.

#### Step 6
Create the table in the database:

    python manage.py syncdb

You should see something like this:

    Creating tables ...
    Creating table notifications_notification
    Installing custom SQL ...
    Installing indexes ...
    Installed 0 object(s) from 0 fixture(s)

#### Step 7
Edit your base template (usually base.html).

Add this where you want the notifications to appear (most commonly, on the top):

    {% if top_notification %}
        <div class="top_notification{% if hide_top_notification %} hide{% endif %}" data-timestamp="{{ top_notification.shown_since_as_timestamp }}">
            <p>{{ top_notification.text }}</p>
            <a href="#" class="dismiss">×</a>
        </div>
    {% endif %}

And add this where you want the “Show notification” link to appear (feel free to replace it by an icon or something else):

    {% if top_notification %}
        <div class="show_notification{% if not hide_top_notification %} hide{% endif %}">
            <a href="#">Show notification</a>
        </div>
    {% endif %}

#### Step 8
Include [jQuery](http://jquery.com/) and [notifications.js](https://github.com/aruseni/django-notifications-sitewide/blob/master/notifications.js).

Like this:

    <script type="text/javascript" src="/static/jquery-1.7.2.min.js"></script>
    <script type="text/javascript" src="/static/notifications.js"></script>

# Example

If you want to make something like what’s on the screenshots, your template will look like this (let’s simplify it as it’s only an example):

    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <link rel="stylesheet" type="text/css" href="/static/style.css">
        <script type="text/javascript" src="/static/jquery-1.7.2.min.js"></script>
        <script type="text/javascript" src="/static/notifications.js"></script>
        <title>Notification test</title>
    </head>
    <body>
    {% load i18n %}
        {% if top_notification %}
            <div class="top_notification{% if hide_top_notification %} hide{% endif %}" data-timestamp="{{ top_notification.shown_since_as_timestamp }}">
                <p>{{ top_notification.text }}</p>
                <a href="#" class="dismiss">×</a>
            </div>
        {% endif %}
        <header>
        <div class="site_name">
            <h1>Notification test</h1>
        </div>
    {% if top_notification %}
        <div class="show_notification{% if not hide_top_notification %} hide{% endif %}">
            <a data-tooltip="{% trans "Show notification" %}" href="#"><i class="icon-exclamation-sign"></i></a>
        </div>
    {% endif %}
        </header>
        <article>
        <p>Some content.</p>
        </article>
    </body>
    </html>

And the CSS will be something like this:

    body {
        color: #f2f2f2;
        background-color: #000000;
        font-size: 16px;
        font-family: Verdana, Arial, Helvetica, sans-serif;
        padding: 0;
        margin: 0;
    }

    [class^="icon-"],
    [class*=" icon-"] {
        display: inline-block;
        width: 14px;
        height: 14px;
        *margin-right: .3em;
        line-height: 14px;
        vertical-align: text-top;
        background-image: url("/static/glyphicons-halflings-white.png");
        background-position: 14px 14px;
        background-repeat: no-repeat;
    }

    [class^="icon-"]:last-child,
    [class*=" icon-"]:last-child {
        *margin-left: 0;
    }

    .icon-exclamation-sign {
        background-position: 0 -120px;
    }

    a[data-tooltip]:link, a[data-tooltip]:visited {
        position: relative;
        text-decoration: none;
        border-bottom: solid 1px;
    }

    a[data-tooltip]:before {
        content: "";
        position: absolute;
        border-bottom: 10px solid rgba(88, 178, 255, 0.6);
        border-left: 15px solid transparent;
        border-right: 15px solid transparent;
        visibility: hidden;
        opacity: 0;
        top: 18px;
        left: -8px;
    }

    a[data-tooltip]:after {
        content: attr(data-tooltip);
        position: absolute;
        color: white;
        top: 28px;
        left: -75px;
        background: rgba(88, 178, 255, 0.6);
        padding: 5px 15px;
        -webkit-border-radius: 5px;
        -moz-border-radius: 5px;
        border-radius: 5px;
        white-space: nowrap;
        visibility: hidden;
        opacity: 0;
    }

    a[data-tooltip]:hover:before, a[data-tooltip]:hover:after {
        visibility: visible;
        opacity: 1;
        -moz-transition: opacity ease-in-out .3s;
    }

    .hide {
      display: none;
    }

    div.top_notification {
        background-color: #a90000;
        color: #ffe8e8;
        font-size: 14px;
        -webkit-box-shadow:inset 0 0 15px #9d0000;
        -moz-box-shadow:inset 0 0 15px #9d0000;
        box-shadow:inset 0 0 15px #9d0000;
    }

    div.top_notification p {
        text-align: center;
        padding: 10px 25px 10px 10px;
        margin: 0;
    }

    div.top_notification a.dismiss {
        position: absolute;
        top: 0;
        right: 10px;
        color: #ffe8e8;
        font-size: 20px;
        text-decoration: none;
    }

    div.top_notification a.dismiss:hover {
        color: #ffffff;
    }

    header {
        height: 150px;
        background: #004349; /* Old browsers */
        background: -moz-linear-gradient(top, #004349 0%, #002b2d 100%); /* FF3.6+ */
        background: -webkit-gradient(linear, left top, left bottom, color-stop(0%,#004349), color-stop(100%,#002b2d)); /* Chrome,Safari4+ */
        background: -webkit-linear-gradient(top, #004349 0%,#002b2d 100%); /* Chrome10+,Safari5.1+ */
        background: -o-linear-gradient(top, #004349 0%,#002b2d 100%); /* Opera 11.10+ */
        background: -ms-linear-gradient(top, #004349 0%,#002b2d 100%); /* IE10+ */
        background: linear-gradient(to bottom, #004349 0%,#002b2d 100%); /* W3C */
        filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#004349', endColorstr='#002b2d',GradientType=0 ); /* IE6-9 */
    }

    header div.site_name {
        padding: 15px 10px 0 15px;
        float: left;
    }

    header div.site_name h1 {
        margin: 0;
    }

    div.show_notification {
        float: left;
        color:white;
        margin-top: 15px;
        position:relative;
        line-height:140%;
    }

    article {
        text-align: center;
        margin-top: 150px;
    }

If you will use the same icon for showing the notification when it was hidden, make sure to also download [glyphicons-halflings-white.png](https://github.com/twitter/bootstrap/blob/master/img/glyphicons-halflings-white.png). Or, if you are using Twitter Bootstrap, you need to change <i class="icon-exclamation-sign"></i> to <i class="icon-exclamation-sign icon-white"></i> and remove the related CSS (`[class^="icon-"], [class*=" icon-"], [class^="icon-"]:last-child, [class*=" icon-"]:last-child, .icon-exclamation-sign`) so it won’t override Bootstrap’s CSS.
