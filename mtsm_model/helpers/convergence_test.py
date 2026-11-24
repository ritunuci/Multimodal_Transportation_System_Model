from colorama import Fore, Style
# The aggregate-level test convergence_test(M_share, M_share_pre) (microtransit mode share), never used and unfinished,
# was removed on 2026-11-23 (docs/open_issues.md, I-16); the run has always used indiv_convergence_test().
def indiv_convergence_test(agent_choice_prob,agent_choice_prob_pre,convergence_gap):
    sum_abs_per_diff=0
    sum_sq_per_diff=0
    sum_sq_diff = 0
    sum_prob=0
    converged=False
    # print(f"{Fore.GREEN}Max agent id is: {max(agent_choice_prob.keys())} and min id is: {min(agent_choice_prob.keys())}{Style.RESET_ALL}")
    for request_id in agent_choice_prob.keys():
        num_modes=len(agent_choice_prob[request_id])
        for i in range(num_modes):
            if agent_choice_prob_pre[request_id][i]==0:
                mode_abs_per_diff=0
            else:
                mode_abs_per_diff=abs(agent_choice_prob[request_id][i] - agent_choice_prob_pre[request_id][i])/agent_choice_prob_pre[request_id][i]
            sum_abs_per_diff+=mode_abs_per_diff

            if agent_choice_prob_pre[request_id][i]==0:
                mode_sq_per_diff=0
            else:
                mode_sq_per_diff=(agent_choice_prob[request_id][i] - agent_choice_prob_pre[request_id][i])**2/agent_choice_prob_pre[request_id][i]
            sum_sq_per_diff+=mode_sq_per_diff

            mode_sq_diff=(agent_choice_prob[request_id][i] - agent_choice_prob_pre[request_id][i]) ** 2
            sum_sq_diff += mode_sq_diff
            #
            sum_prob+=agent_choice_prob_pre[request_id][i]


    per_sq_diff=sum_sq_diff/sum_prob
    # per_abs_diff = sum_abs_diff / sum_prob
    if sum_sq_per_diff<=convergence_gap:
        converged=True

    print("converged:",converged,"sum_abs_per_diff:",sum_abs_per_diff,"sum_sq_per_diff",sum_sq_per_diff,"per_sq_diff",per_sq_diff)

    return converged,sum_sq_per_diff