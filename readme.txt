Made by Nikolina

Quick tutorial for future devs on django features used in this project.

Applications: movies, tvshows, media, services, cinemas, charts, spotlights, \
              lists, genres, distributors
application called other is not currently used in anything, it just contains
some models from old cms.

In current project, apps consists of :
1. models.py file that contains a list of models (tables) used on certain \
   app and/or the whole project in general
2. admin.py file that has the whole logic of this project
2. settings folder that is essential for django to work properly
(other built in django files are not really used, like views.py, because \
 in this project we are only using django admin interface)

Quick pro-tips :
1. debug flag (in base.py) should always be put on False when deploying a project
2. all credentials should be set in heroku config and used as env variables
3. when making a new app, in order it to work, it needs to be put in base.py \
   under INSTALLED_APPS
4. after adding a new model, makemigration + migration is needed (when \
   running the app locally, you might see a msg: You have x unapplied \
   migration(s). so migration should be done)
5. all basic commands can very easily be found in django official tutorial, so \
   use it and go back to it as much as you need

ADMIN.py

class Form:
forms are pages distinctive by the path /<id>/change/ and it contains form \
  fields that are actually table attributes and its values
class form is used for fields customization: putting initial values in form \
  fields, changing the label (field name), adding additional form fields \
  that do not exist in db tables and put custom logic on them, etc

class Filter:
used to create custom filters that are shown on the right side of the objects \
  list (by objects list, I mean for example: admin/movies/movies is a path to \
  show list of movie objects from the table Movies in our database

class Admin:
this is the main class used in admin.py file that connects all custom classes \
  above and can also add custom built in features like:
     list_display: what table attributes you want to show in objects list \
                   (you can also make methods and use them as custom fields)
     search_fields: adding table attributes that objects can be searched by
     actions: adding customized actions when you select multiple objects on the list
method response_change is used to extend action of certain buttons visible \
when editing a certain object's form (add genre button, fetch from tmdb button \
save button, and similar)



