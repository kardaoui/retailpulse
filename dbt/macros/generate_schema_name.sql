{#
  Surcharge la macro par défaut pour utiliser les noms de schéma exacts
  (raw, staging, mart) plutôt que d'ajouter le préfixe du schéma cible.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
