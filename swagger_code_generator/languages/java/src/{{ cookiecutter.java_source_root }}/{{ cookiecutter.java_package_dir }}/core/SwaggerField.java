package {{ cookiecutter.java_package }}.core;

import org.json.JSONArray;
import org.json.JSONObject;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import java.util.List;

public final class SwaggerField {
    private Class<?> jsonType;
    private Class<?> javaType;
    private SwaggerField innerSwaggerField;
    private boolean isRequired;
    private boolean isNullable;
    private SwaggerFormat.Formats format;

    private SwaggerField() {
        this.javaType = null;
        this.innerSwaggerField = null;
        this.isRequired = true;
        this.isNullable = false;
        this.format = SwaggerFormat.Formats.NO_FORMAT;
    }

    public Class<?> getJsonType() {
        return this.jsonType;
    }

    public Class<?> getJavaType() {
        return this.javaType == null ? getJsonType() : this.javaType;
    }

    public SwaggerField getInnerSwaggerField() {
        return this.innerSwaggerField;
    }

    public boolean isRequired() {
        return this.isRequired;
    }

    public boolean isNullable() {
        return this.isNullable;
    }

    public SwaggerFormat.Formats getFormat() {
        return this.format;
    }

    @Override
    public String toString() {
        return this.getClass().getSimpleName() + "[" +
                "jsonType=" + getJsonType().getSimpleName() + "," +
                "javaType=" + getJavaType().getSimpleName() + "," +
                "innerJavaType=" + (getInnerSwaggerField() == null ? null : getInnerSwaggerField()) + "," +
                "isRequired=" + isRequired() + "," +
                "isNullable=" + isNullable() + "," +
                "format=" + getFormat().name() +
                "]";
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.FIELD)
    public @interface Annotation {
        String fieldName();
    }

    public static class Builder {
        private SwaggerField swaggerField = new SwaggerField();

        public Builder setJsonType(Class<?> jsonType) {
            this.swaggerField.jsonType = jsonType;
            return this;
        }

        public Builder setRequired(boolean required) {
            this.swaggerField.isRequired = required;
            return this;
        }

        public Builder setJavaType(Class<?> javaType) {
            this.swaggerField.javaType = javaType;
            return this;
        }

        public Builder setInnerSwaggerField(Builder innerSwaggerFieldBuilder) {
            return setInnerSwaggerField(innerSwaggerFieldBuilder.build());
        }

        public Builder setInnerSwaggerField(SwaggerField innerSwaggerField) {
            this.swaggerField.innerSwaggerField = innerSwaggerField;
            return this;
        }

        public Builder setNullable(boolean nullable) {
            this.swaggerField.isNullable = nullable;
            return this;
        }

        public Builder setFormat(SwaggerFormat.Formats format) {
            this.swaggerField.format = format;
            return this;
        }

        public SwaggerField build() {
            if (this.swaggerField.getFormat() == null) {
                throw new Exception(this.swaggerField, "format is null");
            } else {
                Class tmpType;
                tmpType = this.swaggerField.getFormat().getSwaggerFormat().getJsonType();
                this.swaggerField.jsonType = this.swaggerField.jsonType == null ? tmpType : this.swaggerField.jsonType;
                tmpType = this.swaggerField.getFormat().getSwaggerFormat().getJavaType();
                this.swaggerField.javaType = this.swaggerField.javaType == null ? tmpType : this.swaggerField.javaType;
            }

            if (this.swaggerField.innerSwaggerField != null) {
                this.swaggerField.jsonType = JSONArray.class;
                this.swaggerField.javaType = List.class;
            }

            if (AbstractSwaggerModel.class.isAssignableFrom(this.swaggerField.getJavaType())) {
                this.swaggerField.jsonType = JSONObject.class;
            }


            if (this.swaggerField.getJsonType() == null) {
                throw new Exception(this.swaggerField, "jsonType is null");
            }

            if (this.swaggerField.getJavaType() == null) {
                throw new Exception(this.swaggerField, "javaType is null");
            }
            return this.swaggerField;
        }
    }

    public static class Exception extends RuntimeException {
        public Exception(JSONObject jsonObject, String message) {
            super(message + " JSONObject[" + jsonObject.toString() + "]");
        }

        public Exception(SwaggerField SwaggerField, String message) {
            super(message + " SwaggerField [" + SwaggerField.toString() + "]");
        }

        public Exception(String message) {
            super(message);
        }
    }
}
