class PID:
    """PID Controller
    """

    def __init__(self, P=0.5, I=0, D=0, target=320, init_output=0):

        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.err_pre = 0
        self.err_last = 0
        self.u = 0
        self.integral = 0
        self.ideal = target
        self.last_output = init_output
        self.pre_output = init_output

    def update(self, feedback_value):
        self.err_pre = self.ideal - feedback_value
        self.integral *= 0.86
        self.integral += self.err_pre
        self.u = self.Kp*self.err_pre + self.Ki * \
            self.integral + self.Kd*(self.err_pre-self.err_last)
        self.err_last = self.err_pre
        self.pre_output = self.u
        self.last_output = self.pre_output
        return self.pre_output

    def setKp(self, proportional_gain):
        """Determines how aggressively the PID reacts to the current error with setting Proportional Gain"""
        self.Kp = proportional_gain

    def setKi(self, integral_gain):
        """Determines how aggressively the PID reacts to the current error with setting Integral Gain"""
        self.Ki = integral_gain

    def setKd(self, derivative_gain):
        """Determines how aggressively the PID reacts to the current error with setting Derivative Gain"""
        self.Kd = derivative_gain
