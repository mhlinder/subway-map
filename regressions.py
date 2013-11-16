import statstmodels.formula.api as sm

model = sm.ols(formula='lpop_dens ~ v_larea', data=stops)
fitted = model.fit()
fitted.summary().to_text()
