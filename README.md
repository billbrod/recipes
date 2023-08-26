# recipes

Recipes website

TODO:
- [X] Deploy to custom domain
- [X] if get secret working: add test to make all secret recipes only have
      search exclude in header, no tags
- [X] and that all secrest are included in index
- [X] include secret recipes:
  - [X] do the same cloning trick as in rpg notes
  - [X] run the tests from secret recipes
  - [X] mv it to the secret.hash location before site build
- [X] move secret recipe tests to scripts and include in pre commit hooks
- [ ] Add tags for: entertaining/having guests, effort-level (easy, normal,
      involved)
  - group tags into categories: cuisine, dish, context, protein, ingredient,
    difficulty
- [ ] Add recipes!
- [ ] Add random selection of recipes to the index?
  - can do it based on tags? might need to be on tags page for that
- [ ] Convert trello recipes -- converted, just moving them over now
- [ ] Convert tandoor recipes -- converted, moving over now
- [ ] add bean cooking times from Cool Beans and from [Rancho Gordo
      pdf](https://static1.squarespace.com/static/560ad766e4b0bd9a7a2bdab8/t/5e95f2b52aae8d6545a08797/1586885302075/pressure_cooking.pdf)
- [ ] little "recipes": salt:water ratio for pasta, iced tea, vinegrette, stuff from Ratio?
- [ ] add dad's cocktails on secret page
- [ ] Convert old Food.org file?
    - has some useful tables, links, etc, in addition to recipes
    - way to do this might to re-import any where the source is importable --
      there must be some tool to convert from json schema to markdown or I could
      just extract the schema and then convert it the same way I'm doing from
      tandoor
    - and then for those that aren't importable, do manually / with custom
      converter
