package {{ cookiecutter.java_package }}.core;

import org.apache.commons.lang3.builder.HashCodeBuilder;
import org.json.JSONArray;
import org.json.JSONObject;

import java.util.*;

public abstract class AbstractSwaggerModel<T extends AbstractSwaggerModel> {

    public abstract Map<String, SwaggerField> getSwaggerFields();

    private final Set<String> IS_FIELD_PRESENT = new HashSet<>();

    protected boolean isFieldPresent(String fieldName) {
        return IS_FIELD_PRESENT.contains(fieldName);
    }

    protected void setFieldPresent(String fieldName) {
        IS_FIELD_PRESENT.add(fieldName);
    }

    protected void unsetFieldPresent(String fieldName) {
        set(fieldName, null);
        IS_FIELD_PRESENT.remove(fieldName);
    }

    public T setFromJson(String jsonString) {
        return setFromJson(new JSONObject(jsonString));
    }

    public T setFromJson(JSONObject jsonObject) {
        final Map<String, SwaggerField> swaggerFields = getSwaggerFields();
        for (Map.Entry<String, SwaggerField> entry : swaggerFields.entrySet()) {
            setFromJson(jsonObject, entry.getKey(), entry.getValue());
        }
        @SuppressWarnings("unchecked")
        T t = (T) this;
        return t;
    }

    private void setFromJson(JSONObject jsonObject, String fieldName, SwaggerField fieldSpecification) {

        Object jsonValue = jsonObject.opt(fieldName);
        if (jsonValue == null && fieldSpecification.isRequired()) {
            throw new SwaggerField.Exception(jsonObject, fieldName + " is required");
        } else if (jsonValue == JSONObject.NULL && !fieldSpecification.isNullable()) {
            throw new SwaggerField.Exception(jsonObject, fieldName + " is not nullable");
        } else if (jsonValue != null && jsonValue != JSONObject.NULL) {
            if (fieldSpecification.getJsonType() == Long.class && jsonValue.getClass() == Integer.class) {
                jsonValue = new Long((Integer) jsonValue);
            }
            if (!fieldSpecification.getJsonType().isInstance(jsonValue)) {
                throw new SwaggerField.Exception(jsonObject, fieldName + " is not a " + fieldSpecification.getJsonType().getSimpleName());
            }
        }

        Object javaValue;
        if (jsonValue == null) {
            return;
        } else if (jsonValue == JSONObject.NULL) {
            javaValue = null;
        } else if (jsonValue instanceof JSONArray) {
            final List list = new ArrayList(((JSONArray) jsonValue).length());
            for (Object listItem : ((JSONArray) jsonValue)) {
                list.add(fieldSpecification.getInnerSwaggerField().getFormat().getSwaggerFormat().parse(fieldSpecification.getInnerSwaggerField().getJavaType(), listItem));
            }
            javaValue = list;
        } else {
            javaValue = fieldSpecification.getFormat().getSwaggerFormat().parse(fieldSpecification.getJavaType(), jsonValue);
        }

        set(fieldName, javaValue);
        if (!fieldSpecification.isRequired()) {
            setFieldPresent(fieldName);
        }
    }

    protected abstract void set(String fieldName, Object object);

    protected abstract Object get(String fieldName) throws IllegalStateException;

    protected Object getSafe(String fieldName, Object defaultValue) {
        try {
            return get(fieldName);
        } catch (IllegalStateException ignore) {
            return defaultValue;
        }
    }

    private void putToJson(JSONObject jsonObject, String fieldName, SwaggerField fieldSpecification) {
        final Object defaultValue = new Object();
        final Object javaValue = getSafe(fieldName, defaultValue);

        if (javaValue == defaultValue) {
            if (fieldSpecification.isRequired()) {
                throw new SwaggerField.Exception(fieldName + " is a required field.");
            }
            return;
        }

        if (javaValue == null) {
            if (fieldSpecification.isRequired() && !fieldSpecification.isNullable()) {
                throw new SwaggerField.Exception(fieldName + " is a not nullable and required field.");
            }
            if (!fieldSpecification.isRequired() && !isFieldPresent(fieldName)) {
                return;
            }
        }

        Object jsonValue;
        if (javaValue instanceof List) {
            final JSONArray jsonArray = new JSONArray();
            for (Object listItem : (List) javaValue) {
                jsonArray.put(fieldSpecification.getInnerSwaggerField().getFormat().getSwaggerFormat().format(listItem));
            }
            jsonValue = jsonArray;
        } else {
            jsonValue = fieldSpecification.getFormat().getSwaggerFormat().format(javaValue);
            if (jsonValue == null) {
                jsonValue = JSONObject.NULL;
            }
        }
        jsonObject.put(fieldName, jsonValue);
    }


    public JSONObject getJson() {
        final JSONObject jsonObject = new JSONObject();
        final Map<String, SwaggerField> swaggerFields = getSwaggerFields();
        for (Map.Entry<String, SwaggerField> entry : swaggerFields.entrySet()) {
            putToJson(jsonObject, entry.getKey(), entry.getValue());
        }
        return jsonObject;
    }

    protected TreeSet<String> getSwaggerFieldNames() {
        return new TreeSet<>(getSwaggerFields().keySet());
    }


    @Override
    public boolean equals(Object object) {
        if (object == null) {
            return false;
        }

        if (object == this) {
            return true;
        }

        if (!object.getClass().isAssignableFrom(getClass())) {
            return false;
        }

        final AbstractSwaggerModel that = (AbstractSwaggerModel) object;
        for (String fieldName : this.getSwaggerFieldNames()) {
            if (!Objects.equals(this.get(fieldName), that.get(fieldName))) {
                return false;
            }
        }
        return true;
    }

    @Override
    public int hashCode() {
        HashCodeBuilder hashCodeBuilder = new HashCodeBuilder();
        for (String fieldName : this.getSwaggerFieldNames()) {
            hashCodeBuilder.append(get(fieldName));
        }
        return hashCodeBuilder.hashCode();
    }

    @Override
    public String toString() {
        return getJson().toString();
    }
}
