package {{ cookiecutter.java_package }}.core;

import org.json.JSONObject;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

public abstract class SwaggerFormat<JAVA, JSON> {
    public abstract Class<JAVA> getJavaType();

    public abstract Class<JSON> getJsonType();

    protected abstract JAVA internalParse(JSON object) throws Exception;

    public JAVA parse(Object object) throws Exception {
        return parse(null, object);
    }

    public JAVA parse(Class<?> javaClass, Object object) throws Exception {
        if (object == null) {
            return null;
        }

        if (javaClass != null) {
            if (AbstractSwaggerModel.class.isAssignableFrom(javaClass)) {
                try {
                    AbstractSwaggerModel swaggerModel = (AbstractSwaggerModel) javaClass.newInstance();
                    swaggerModel.setFromJson((JSONObject) object);
                    @SuppressWarnings("unchecked")
                    JAVA java = (JAVA) swaggerModel;
                    return java;
                } catch (InstantiationException | IllegalAccessException e) {
                    throw new RuntimeException("To understand when it could happen");
                }
            } else if (Enum.class.isAssignableFrom(javaClass)) {
                final Enum enumValue = Enum.valueOf((Class<Enum>) javaClass, (String) object);
                @SuppressWarnings("unchecked")
                JAVA java = (JAVA) enumValue;
                return java;
            }
        }

        Class<JSON> jsonType = getJsonType();
        if (jsonType == null) {
            @SuppressWarnings("unchecked")
            JAVA java = (JAVA) object;
            return java;
        }
        try {
            return internalParse(jsonType.cast(object));
        } catch (ClassCastException classCastException) {
            throw new Exception(classCastException);
        }
    }

    protected abstract JSON internalFormat(JAVA object) throws Exception;

    public JSON format(Object object) throws Exception {
        if (object == null) {
            return null;
        }

        if (object instanceof AbstractSwaggerModel) {
            @SuppressWarnings("unchecked")
            JSON json = (JSON) ((AbstractSwaggerModel) object).getJson();
            return json;
        }

        if (object instanceof Enum) {
            @SuppressWarnings("unchecked")
            JSON json = (JSON) ((Enum) object).name();
            return json;
        }

        Class<JAVA> javaType = getJavaType();
        if (javaType == null) {
            @SuppressWarnings("unchecked")
            JSON json = (JSON) object;
            return json;
        }
        try {
            return internalFormat(javaType.cast(object));
        } catch (ClassCastException classCastException) {
            throw new Exception(classCastException);
        }
    }


    public static class Exception extends RuntimeException {
        public Exception(Throwable cause) {
            super(cause);
        }
    }

    public enum Formats {
        NO_FORMAT(new SwaggerFormat() {
            @Override
            public Class getJavaType() {
                return null;
            }

            @Override
            public Class getJsonType() {
                return null;
            }

            @Override
            protected Object internalParse(Object object) throws Exception {
                return null;
            }

            @Override
            protected Object internalFormat(Object object) throws Exception {
                return null;
            }
        }),
        ENUM(new SwaggerFormat<Enum, String>() {
            @Override
            public Class<Enum> getJavaType() {
                return Enum.class;
            }

            @Override
            public Class<String> getJsonType() {
                return String.class;
            }

            @Override
            protected Enum internalParse(String object) throws Exception {
                return null;
            }

            @Override
            protected String internalFormat(Enum object) throws Exception {
                return null;
            }
        }),
        DATE(new SwaggerFormat<Date, String>() {
            private final SimpleDateFormat ISO8601_DATE_PARSER = new SimpleDateFormat("yyyy-MM-dd");

            @Override
            public Class<Date> getJavaType() {
                return Date.class;
            }

            @Override
            public Class<String> getJsonType() {
                return String.class;
            }

            @Override
            protected Date internalParse(String object) throws Exception {
                try {
                    return ISO8601_DATE_PARSER.parse(object);
                } catch (ParseException e) {
                    throw new Exception(e);
                }
            }

            @Override
            protected String internalFormat(Date object) throws Exception {
                return ISO8601_DATE_PARSER.format(object);
            }
        });

        private final SwaggerFormat swaggerFormat;

        Formats(SwaggerFormat swaggerFormat) {
            this.swaggerFormat = swaggerFormat;
        }

        public SwaggerFormat getSwaggerFormat() {
            return this.swaggerFormat;
        }
    }
}
